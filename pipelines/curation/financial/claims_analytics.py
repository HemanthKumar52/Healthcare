"""Gold layer curation: Claims Analytics.

Joins bronze billing, insurance claims, and payments to produce
claims analytics with denial rates and payment metrics.

Output: healthcare_marketplace.financial.claims_analytics
"""

import sys
from pathlib import Path

from pyspark.sql import functions as F
from pyspark.sql.window import Window

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from utils.spark_session import get_spark_session
from utils.unity_catalog import (
    create_schema_if_not_exists,
    set_table_comment,
    set_table_tags,
)

CATALOG = "healthcare_marketplace"
SCHEMA = "financial"
TABLE = "claims_analytics"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"

BRONZE_BILLING = f"{CATALOG}.bronze.raw_billing"
BRONZE_INSURANCE_CLAIMS = f"{CATALOG}.bronze.raw_insurance_claims"
BRONZE_PAYMENTS = f"{CATALOG}.bronze.raw_payments"


def build_claims_analytics(spark) -> None:
    """Build the claims analytics gold table.

    Joins billing records with insurance claims and payments to compute
    total billed, total paid, denial rates, average payment time, and
    identifies top denial reasons.
    """
    billing = spark.table(BRONZE_BILLING)
    claims = spark.table(BRONZE_INSURANCE_CLAIMS)
    payments = spark.table(BRONZE_PAYMENTS)

    # Aggregate payments per billing record
    payment_summary = (
        payments.groupBy("billing_id")
        .agg(
            F.sum("amount").alias("total_paid"),
            F.count("*").alias("payment_count"),
            F.min("payment_date").alias("first_payment_date"),
            F.max("payment_date").alias("last_payment_date"),
            F.collect_set("payment_method").alias("payment_methods"),
        )
        .withColumnRenamed("billing_id", "pay_billing_id")
    )

    # Join billing with claims
    result = billing.join(
        claims.select(
            F.col("billing_id").alias("claim_billing_id"),
            "claim_id",
            "claim_status",
            "claim_date",
            "submitted_date",
            "adjudication_date",
            "denial_reason",
            "insurance_provider",
            "coverage_amount",
        ),
        billing["billing_id"] == F.col("claim_billing_id"),
        "left",
    ).drop("claim_billing_id")

    # Join with payment summary
    result = result.join(
        payment_summary,
        billing["billing_id"] == payment_summary["pay_billing_id"],
        "left",
    ).drop("pay_billing_id")

    # Compute claim denial flag
    result = result.withColumn(
        "is_denied",
        F.when(
            F.lower(F.col("claim_status")).isin("denied", "rejected"),
            F.lit(True),
        ).otherwise(F.lit(False)),
    )

    # Compute partially paid flag
    result = result.withColumn(
        "is_partially_paid",
        F.when(
            F.col("total_paid").isNotNull()
            & F.col("total_amount").isNotNull()
            & (F.col("total_paid") > 0)
            & (F.col("total_paid") < F.col("total_amount")),
            F.lit(True),
        ).otherwise(F.lit(False)),
    )

    # Compute days to first payment
    result = result.withColumn(
        "days_to_first_payment",
        F.when(
            F.col("billing_date").isNotNull()
            & F.col("first_payment_date").isNotNull(),
            F.datediff(F.col("first_payment_date"), F.col("billing_date")),
        ).otherwise(F.lit(None)),
    )

    # Compute days to adjudication
    result = result.withColumn(
        "days_to_adjudication",
        F.when(
            F.col("submitted_date").isNotNull()
            & F.col("adjudication_date").isNotNull(),
            F.datediff(F.col("adjudication_date"), F.col("submitted_date")),
        ).otherwise(F.lit(None)),
    )

    # Compute outstanding balance
    result = result.withColumn(
        "outstanding_balance",
        F.when(
            F.col("total_amount").isNotNull(),
            F.col("total_amount") - F.coalesce(F.col("total_paid"), F.lit(0)),
        ).otherwise(F.lit(None)),
    )

    # Compute collection rate per record
    result = result.withColumn(
        "collection_rate",
        F.when(
            F.col("total_amount").isNotNull() & (F.col("total_amount") > 0),
            F.round(
                F.coalesce(F.col("total_paid"), F.lit(0)) / F.col("total_amount"), 4
            ),
        ).otherwise(F.lit(None)),
    )

    # Fill nulls
    result = result.fillna({"total_paid": 0.0, "payment_count": 0})

    # Select final columns
    result = result.select(
        "billing_id",
        "patient_id",
        "encounter_id",
        "claim_id",
        "billing_date",
        "service_date",
        "total_amount",
        "total_paid",
        "outstanding_balance",
        "collection_rate",
        "insurance_provider",
        "coverage_amount",
        "claim_status",
        "is_denied",
        "denial_reason",
        "is_partially_paid",
        "submitted_date",
        "adjudication_date",
        "days_to_adjudication",
        "first_payment_date",
        "last_payment_date",
        "days_to_first_payment",
        "payment_count",
        "payment_methods",
        F.current_timestamp().alias("_processed_at"),
    )

    # Write gold table
    (
        result.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(FULL_TABLE)
    )

    row_count = spark.table(FULL_TABLE).count()
    print(f"[DONE] {FULL_TABLE}: {row_count:,} rows written")

    # Compute and print summary statistics
    summary = spark.table(FULL_TABLE).agg(
        F.sum("total_amount").alias("total_billed"),
        F.sum("total_paid").alias("total_collected"),
        F.avg("days_to_first_payment").alias("avg_payment_time_days"),
        F.avg(F.col("is_denied").cast("int")).alias("denial_rate"),
    ).collect()[0]

    print(f"       Total Billed:  ${summary['total_billed']:,.2f}" if summary["total_billed"] else "")
    print(f"       Total Paid:    ${summary['total_collected']:,.2f}" if summary["total_collected"] else "")
    print(f"       Denial Rate:   {summary['denial_rate']:.2%}" if summary["denial_rate"] else "")
    print(f"       Avg Pay Time:  {summary['avg_payment_time_days']:.1f} days" if summary["avg_payment_time_days"] else "")

    # Unity Catalog metadata
    try:
        set_table_comment(
            spark,
            FULL_TABLE,
            "Claims analytics combining billing, insurance claims, and payments "
            "with denial rates, collection rates, and payment timing metrics.",
        )
        set_table_tags(
            spark,
            FULL_TABLE,
            {
                "domain": "financial",
                "layer": "gold",
                "contains_phi": "true",
                "owner": "revenue-cycle-team",
                "refresh_cadence": "daily",
            },
        )
    except Exception as e:
        print(f"[WARN] Could not set UC metadata: {e}")


def main() -> None:
    """Entry point for the claims analytics curation pipeline."""
    spark = get_spark_session("GoldCuration_ClaimsAnalytics")

    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception as e:
        print(f"[WARN] Could not create schema via UC: {e}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")

    build_claims_analytics(spark)
    spark.stop()


if __name__ == "__main__":
    main()
