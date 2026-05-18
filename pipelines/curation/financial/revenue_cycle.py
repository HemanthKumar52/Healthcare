"""Gold layer curation: Revenue Cycle.

Joins bronze billing and payments to produce revenue cycle metrics
including days in accounts receivable and collection rates.

Output: healthcare_marketplace.financial.revenue_cycle
"""

import sys
from pathlib import Path

from pyspark.sql import functions as F

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from utils.spark_session import get_spark_session
from utils.unity_catalog import (
    create_schema_if_not_exists,
    set_table_comment,
    set_table_tags,
)

CATALOG = "healthcare_marketplace"
SCHEMA = "financial"
TABLE = "revenue_cycle"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"

BRONZE_BILLING = f"{CATALOG}.bronze.raw_billing"
BRONZE_PAYMENTS = f"{CATALOG}.bronze.raw_payments"


def build_revenue_cycle(spark) -> None:
    """Build the revenue cycle gold table.

    Computes days in accounts receivable, collection rates, revenue
    by department, and payment method breakdown from billing and
    payment records.
    """
    billing = spark.table(BRONZE_BILLING)
    payments = spark.table(BRONZE_PAYMENTS)

    # Aggregate payments per billing record
    payment_agg = (
        payments.groupBy("billing_id")
        .agg(
            F.sum("amount").alias("total_paid"),
            F.count("*").alias("payment_count"),
            F.min("payment_date").alias("first_payment_date"),
            F.max("payment_date").alias("last_payment_date"),
        )
        .withColumnRenamed("billing_id", "pay_billing_id")
    )

    # Payment method breakdown per billing record
    payment_methods = (
        payments.groupBy("billing_id", "payment_method")
        .agg(F.sum("amount").alias("method_amount"))
        .groupBy("billing_id")
        .agg(
            F.map_from_entries(
                F.collect_list(
                    F.struct(F.col("payment_method"), F.col("method_amount"))
                )
            ).alias("payment_method_breakdown")
        )
        .withColumnRenamed("billing_id", "pm_billing_id")
    )

    # Join billing with payment aggregates
    result = billing.join(
        payment_agg,
        billing["billing_id"] == payment_agg["pay_billing_id"],
        "left",
    ).drop("pay_billing_id")

    result = result.join(
        payment_methods,
        billing["billing_id"] == payment_methods["pm_billing_id"],
        "left",
    ).drop("pm_billing_id")

    # Fill null payments
    result = result.fillna({"total_paid": 0.0, "payment_count": 0})

    # Compute days in accounts receivable
    result = result.withColumn(
        "days_in_ar",
        F.when(
            F.col("billing_date").isNotNull() & F.col("last_payment_date").isNotNull(),
            F.datediff(F.col("last_payment_date"), F.col("billing_date")),
        ).when(
            F.col("billing_date").isNotNull() & (F.col("total_paid") == 0),
            F.datediff(F.current_date(), F.col("billing_date")),
        ).otherwise(F.lit(None)),
    )

    # Compute collection rate
    result = result.withColumn(
        "collection_rate",
        F.when(
            F.col("total_amount").isNotNull() & (F.col("total_amount") > 0),
            F.round(F.col("total_paid") / F.col("total_amount"), 4),
        ).otherwise(F.lit(0.0)),
    )

    # Compute outstanding balance
    result = result.withColumn(
        "outstanding_balance",
        F.when(
            F.col("total_amount").isNotNull(),
            F.greatest(
                F.col("total_amount") - F.col("total_paid"), F.lit(0)
            ),
        ).otherwise(F.lit(0.0)),
    )

    # Aging bucket classification
    result = result.withColumn(
        "ar_aging_bucket",
        F.when(F.col("collection_rate") >= 1.0, F.lit("Paid in Full"))
        .when(F.col("days_in_ar").isNull(), F.lit("Unknown"))
        .when(F.col("days_in_ar") <= 30, F.lit("0-30 days"))
        .when(F.col("days_in_ar") <= 60, F.lit("31-60 days"))
        .when(F.col("days_in_ar") <= 90, F.lit("61-90 days"))
        .when(F.col("days_in_ar") <= 120, F.lit("91-120 days"))
        .otherwise(F.lit("120+ days")),
    )

    # Billing month for trend analysis
    result = result.withColumn(
        "billing_month",
        F.date_trunc("month", F.col("billing_date")),
    )

    # Select final columns
    result = result.select(
        "billing_id",
        "patient_id",
        "encounter_id",
        "department_id",
        "billing_date",
        "billing_month",
        "service_date",
        "due_date",
        "total_amount",
        "total_paid",
        "outstanding_balance",
        "collection_rate",
        "days_in_ar",
        "ar_aging_bucket",
        "first_payment_date",
        "last_payment_date",
        "payment_count",
        "payment_method_breakdown",
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

    # Print summary by aging bucket
    print("\n  AR Aging Distribution:")
    aging_dist = (
        spark.table(FULL_TABLE)
        .groupBy("ar_aging_bucket")
        .agg(
            F.count("*").alias("count"),
            F.sum("outstanding_balance").alias("total_outstanding"),
        )
        .orderBy("ar_aging_bucket")
        .collect()
    )
    for row in aging_dist:
        print(
            f"    {row['ar_aging_bucket']:>15}: "
            f"{row['count']:>6,} records, "
            f"${row['total_outstanding']:>12,.2f} outstanding"
        )

    # Unity Catalog metadata
    try:
        set_table_comment(
            spark,
            FULL_TABLE,
            "Revenue cycle metrics including days in accounts receivable, "
            "collection rates, aging buckets, and payment method breakdowns.",
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
    """Entry point for the revenue cycle curation pipeline."""
    spark = get_spark_session("GoldCuration_RevenueCycle")

    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception as e:
        print(f"[WARN] Could not create schema via UC: {e}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")

    build_revenue_cycle(spark)
    spark.stop()


if __name__ == "__main__":
    main()
