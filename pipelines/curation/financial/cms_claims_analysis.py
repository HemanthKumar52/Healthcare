"""Gold layer curation: CMS Claims Analysis.

Joins CMS beneficiary, inpatient, and outpatient claims to produce
a comprehensive Medicare claims analysis data product.

Output: healthcare_marketplace.financial.cms_claims_analysis
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
TABLE = "cms_claims_analysis"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"


def build_cms_claims_analysis(spark) -> None:
    """Build CMS claims analysis gold table.

    Combines inpatient and outpatient claims with beneficiary demographics
    to produce a unified claims view with cost analysis, utilization
    metrics, and chronic condition flags.
    """
    beneficiaries = spark.table(f"{CATALOG}.bronze.cms_beneficiary_summary")
    inpatient = spark.table(f"{CATALOG}.bronze.cms_inpatient_claims")
    outpatient = spark.table(f"{CATALOG}.bronze.cms_outpatient_claims")

    # ── Inpatient Claims Summary per Beneficiary ────────────
    ip_summary = (
        inpatient.groupBy("DESYNPUF_ID")
        .agg(
            F.count("CLM_ID").alias("ip_claim_count"),
            F.sum("CLM_PMT_AMT").alias("ip_total_payment"),
            F.avg("CLM_PMT_AMT").alias("ip_avg_payment"),
            F.sum("CLM_UTLZTN_DAY_CNT").alias("ip_total_days"),
            F.avg("CLM_UTLZTN_DAY_CNT").alias("ip_avg_los"),
            F.min("CLM_FROM_DT").alias("ip_first_claim_date"),
            F.max("CLM_THRU_DT").alias("ip_last_claim_date"),
            F.sum("NCH_BENE_IP_DDCTBL_AMT").alias("ip_total_deductible"),
            F.sum("NCH_BENE_PTA_COINSRNC_LBLTY_AM").alias("ip_total_coinsurance"),
            F.countDistinct("PRVDR_NUM").alias("ip_unique_providers"),
            F.countDistinct("ADMTNG_ICD9_DGNS_CD").alias("ip_unique_diagnoses"),
        )
        .withColumnRenamed("DESYNPUF_ID", "ip_bene_id")
    )

    # ── Outpatient Claims Summary per Beneficiary ───────────
    op_summary = (
        outpatient.groupBy("DESYNPUF_ID")
        .agg(
            F.count("CLM_ID").alias("op_claim_count"),
            F.sum("CLM_PMT_AMT").alias("op_total_payment"),
            F.avg("CLM_PMT_AMT").alias("op_avg_payment"),
            F.min("CLM_FROM_DT").alias("op_first_claim_date"),
            F.max("CLM_THRU_DT").alias("op_last_claim_date"),
            F.sum("NCH_BENE_PTB_DDCTBL_AMT").alias("op_total_deductible"),
            F.sum("NCH_BENE_PTB_COINSRNC_AMT").alias("op_total_coinsurance"),
            F.countDistinct("PRVDR_NUM").alias("op_unique_providers"),
        )
        .withColumnRenamed("DESYNPUF_ID", "op_bene_id")
    )

    # ── Join with Beneficiary Demographics ──────────────────
    result = beneficiaries.join(
        ip_summary,
        beneficiaries["DESYNPUF_ID"] == ip_summary["ip_bene_id"],
        "left",
    ).drop("ip_bene_id")

    result = result.join(
        op_summary,
        beneficiaries["DESYNPUF_ID"] == op_summary["op_bene_id"],
        "left",
    ).drop("op_bene_id")

    # Fill nulls for beneficiaries with no claims
    result = result.fillna({
        "ip_claim_count": 0, "ip_total_payment": 0.0, "ip_avg_payment": 0.0,
        "ip_total_days": 0, "ip_avg_los": 0.0, "ip_total_deductible": 0.0,
        "ip_total_coinsurance": 0.0, "ip_unique_providers": 0, "ip_unique_diagnoses": 0,
        "op_claim_count": 0, "op_total_payment": 0.0, "op_avg_payment": 0.0,
        "op_total_deductible": 0.0, "op_total_coinsurance": 0.0, "op_unique_providers": 0,
    })

    # ── Derived Metrics ─────────────────────────────────────
    result = (
        result
        .withColumn("total_claim_count", F.col("ip_claim_count") + F.col("op_claim_count"))
        .withColumn("total_payment", F.col("ip_total_payment") + F.col("op_total_payment"))
        .withColumn("total_deductible", F.col("ip_total_deductible") + F.col("op_total_deductible"))
        .withColumn("total_coinsurance", F.col("ip_total_coinsurance") + F.col("op_total_coinsurance"))
        .withColumn("total_oop", F.col("total_deductible") + F.col("total_coinsurance"))
        # Chronic condition count
        .withColumn("chronic_condition_count",
            F.when(F.col("SP_ALZHDMTA") == 1, 1).otherwise(0) +
            F.when(F.col("SP_CHF") == 1, 1).otherwise(0) +
            F.when(F.col("SP_CHRNKIDN") == 1, 1).otherwise(0) +
            F.when(F.col("SP_CNCR") == 1, 1).otherwise(0) +
            F.when(F.col("SP_COPD") == 1, 1).otherwise(0) +
            F.when(F.col("SP_DEPRESSN") == 1, 1).otherwise(0) +
            F.when(F.col("SP_DIABETES") == 1, 1).otherwise(0) +
            F.when(F.col("SP_ISCHMCHT") == 1, 1).otherwise(0) +
            F.when(F.col("SP_OSTEOPRS") == 1, 1).otherwise(0) +
            F.when(F.col("SP_RA_OA") == 1, 1).otherwise(0) +
            F.when(F.col("SP_STRKETIA") == 1, 1).otherwise(0)
        )
        # Risk tier
        .withColumn("risk_tier",
            F.when(F.col("chronic_condition_count") >= 5, "High")
            .when(F.col("chronic_condition_count") >= 3, "Medium")
            .when(F.col("chronic_condition_count") >= 1, "Low")
            .otherwise("Healthy")
        )
        # Gender label
        .withColumn("gender", F.when(F.col("BENE_SEX_IDENT_CD") == 1, "Male").otherwise("Female"))
        # Race label
        .withColumn("race",
            F.when(F.col("BENE_RACE_CD") == 1, "White")
            .when(F.col("BENE_RACE_CD") == 2, "Black")
            .when(F.col("BENE_RACE_CD") == 3, "Other")
            .when(F.col("BENE_RACE_CD") == 5, "Hispanic")
            .otherwise("Unknown")
        )
        # Is deceased
        .withColumn("is_deceased", F.col("BENE_DEATH_DT").isNotNull())
        .withColumn("_processed_at", F.current_timestamp())
    )

    # ── Select Final Columns ────────────────────────────────
    result = result.select(
        "DESYNPUF_ID", "gender", "race", "SP_STATE_CODE", "BENE_COUNTY_CD",
        "is_deceased", "BENE_HI_CVRAGE_TOT_MONS", "BENE_SMI_CVRAGE_TOT_MONS",
        "chronic_condition_count", "risk_tier",
        "SP_ALZHDMTA", "SP_CHF", "SP_CHRNKIDN", "SP_CNCR", "SP_COPD",
        "SP_DEPRESSN", "SP_DIABETES", "SP_ISCHMCHT", "SP_OSTEOPRS", "SP_RA_OA", "SP_STRKETIA",
        "ip_claim_count", "ip_total_payment", "ip_avg_payment", "ip_total_days", "ip_avg_los",
        "ip_unique_providers", "ip_unique_diagnoses",
        "op_claim_count", "op_total_payment", "op_avg_payment", "op_unique_providers",
        "total_claim_count", "total_payment", "total_deductible", "total_coinsurance", "total_oop",
        "MEDREIMB_IP", "MEDREIMB_OP", "MEDREIMB_CAR",
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

    # Print risk tier distribution
    print("\n  Risk Tier Distribution:")
    tiers = (
        spark.table(FULL_TABLE)
        .groupBy("risk_tier")
        .agg(F.count("*").alias("count"), F.avg("total_payment").alias("avg_cost"))
        .orderBy("risk_tier")
        .collect()
    )
    for row in tiers:
        print(f"    {row['risk_tier']:>10}: {row['count']:>6,} beneficiaries, avg cost ${row['avg_cost']:>10,.2f}")

    try:
        set_table_comment(spark, FULL_TABLE,
            "CMS Medicare claims analysis combining beneficiary demographics, "
            "chronic conditions, inpatient/outpatient utilization, and cost metrics.")
        set_table_tags(spark, FULL_TABLE, {
            "domain": "financial", "layer": "gold", "source": "cms_de_synpuf",
            "contains_phi": "false", "owner": "revenue-cycle-team", "refresh_cadence": "monthly",
        })
    except Exception as e:
        print(f"  [WARN] Could not set UC metadata: {e}")


def main() -> None:
    spark = get_spark_session("GoldCuration_CMSClaimsAnalysis")
    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception:
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")
    build_cms_claims_analysis(spark)
    spark.stop()


if __name__ == "__main__":
    main()
