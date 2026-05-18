"""Gold layer curation: CMS Prescription Drug Analysis.

Analyzes CMS prescription drug events with beneficiary demographics
to produce drug utilization and cost insights.

Output: healthcare_marketplace.financial.cms_prescription_analysis
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
TABLE = "cms_prescription_analysis"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"


def build_cms_prescription_analysis(spark) -> None:
    """Build CMS prescription drug analysis gold table."""
    beneficiaries = spark.table(f"{CATALOG}.bronze.cms_beneficiary_summary")
    prescriptions = spark.table(f"{CATALOG}.bronze.cms_prescription_events")

    # Aggregate per beneficiary
    rx_per_bene = (
        prescriptions.groupBy("DESYNPUF_ID")
        .agg(
            F.count("PDE_ID").alias("total_prescriptions"),
            F.countDistinct("PROD_SRVC_ID").alias("unique_drugs"),
            F.countDistinct("DRUG_NAME").alias("unique_drug_names"),
            F.sum("TOT_RX_CST_AMT").alias("total_rx_cost"),
            F.sum("PTNT_PAY_AMT").alias("total_patient_pay"),
            F.avg("TOT_RX_CST_AMT").alias("avg_rx_cost"),
            F.avg("DAYS_SUPLY_NUM").alias("avg_days_supply"),
            F.sum("QTY_DSPNSD_NUM").alias("total_qty_dispensed"),
            F.min("SRVC_DT").alias("first_rx_date"),
            F.max("SRVC_DT").alias("last_rx_date"),
            F.countDistinct("PRSCRBR_ID").alias("unique_prescribers"),
        )
        .withColumnRenamed("DESYNPUF_ID", "rx_bene_id")
    )

    # Top drug per beneficiary
    drug_counts = (
        prescriptions.groupBy("DESYNPUF_ID", "DRUG_NAME")
        .agg(F.count("*").alias("drug_count"))
    )
    w = Window.partitionBy("DESYNPUF_ID").orderBy(F.desc("drug_count"))
    top_drug = (
        drug_counts.withColumn("rank", F.row_number().over(w))
        .filter(F.col("rank") == 1)
        .select(
            F.col("DESYNPUF_ID").alias("td_bene_id"),
            F.col("DRUG_NAME").alias("most_prescribed_drug"),
        )
    )

    # Join with beneficiary
    result = beneficiaries.select(
        "DESYNPUF_ID", "BENE_SEX_IDENT_CD", "BENE_RACE_CD", "SP_STATE_CODE",
        "SP_DIABETES", "SP_CHF", "SP_COPD", "SP_DEPRESSN",
    ).join(
        rx_per_bene,
        F.col("DESYNPUF_ID") == rx_per_bene["rx_bene_id"],
        "inner",
    ).drop("rx_bene_id")

    result = result.join(
        top_drug,
        F.col("DESYNPUF_ID") == top_drug["td_bene_id"],
        "left",
    ).drop("td_bene_id")

    # Derived metrics
    result = (
        result
        .withColumn("gender", F.when(F.col("BENE_SEX_IDENT_CD") == 1, "Male").otherwise("Female"))
        .withColumn("polypharmacy_flag",
            F.when(F.col("unique_drugs") >= 5, "Yes").otherwise("No"))
        .withColumn("high_cost_flag",
            F.when(F.col("total_rx_cost") > 10000, "Yes").otherwise("No"))
        .withColumn("insurance_coverage_pct",
            F.when(F.col("total_rx_cost") > 0,
                F.round((F.col("total_rx_cost") - F.col("total_patient_pay")) / F.col("total_rx_cost") * 100, 2)
            ).otherwise(0))
        .withColumn("_processed_at", F.current_timestamp())
    )

    result = result.select(
        "DESYNPUF_ID", "gender", "SP_STATE_CODE",
        "SP_DIABETES", "SP_CHF", "SP_COPD", "SP_DEPRESSN",
        "total_prescriptions", "unique_drugs", "unique_drug_names",
        "total_rx_cost", "total_patient_pay", "avg_rx_cost", "avg_days_supply",
        "total_qty_dispensed", "unique_prescribers",
        "most_prescribed_drug", "polypharmacy_flag", "high_cost_flag",
        "insurance_coverage_pct", "first_rx_date", "last_rx_date",
        "_processed_at",
    )

    (
        result.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(FULL_TABLE)
    )

    row_count = spark.table(FULL_TABLE).count()
    print(f"[DONE] {FULL_TABLE}: {row_count:,} rows written")

    try:
        set_table_comment(spark, FULL_TABLE,
            "CMS prescription drug analysis with per-beneficiary utilization, "
            "cost metrics, polypharmacy flags, and top drug identification.")
        set_table_tags(spark, FULL_TABLE, {
            "domain": "financial", "layer": "gold", "source": "cms_de_synpuf",
            "contains_phi": "false", "owner": "pharmacy-analytics-team", "refresh_cadence": "monthly",
        })
    except Exception as e:
        print(f"  [WARN] Could not set UC metadata: {e}")


def main() -> None:
    spark = get_spark_session("GoldCuration_CMSPrescriptionAnalysis")
    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception:
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")
    build_cms_prescription_analysis(spark)
    spark.stop()


if __name__ == "__main__":
    main()
