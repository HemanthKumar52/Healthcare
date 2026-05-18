"""Gold layer curation: Lab Analytics.

Joins bronze lab results with patient demographics to produce an enriched
lab analytics table with abnormal flags and test categorization.

Output: healthcare_marketplace.clinical.lab_analytics
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
SCHEMA = "clinical"
TABLE = "lab_analytics"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"

BRONZE_LAB_RESULTS = f"{CATALOG}.bronze.raw_lab_results"
BRONZE_PATIENTS = f"{CATALOG}.bronze.raw_patients"

# Mapping of common lab test name patterns to categories
TEST_CATEGORIES = {
    "glucose": "Metabolic",
    "hemoglobin": "Hematology",
    "hba1c": "Metabolic",
    "cholesterol": "Lipid Panel",
    "triglyceride": "Lipid Panel",
    "ldl": "Lipid Panel",
    "hdl": "Lipid Panel",
    "creatinine": "Renal",
    "bun": "Renal",
    "gfr": "Renal",
    "alt": "Liver",
    "ast": "Liver",
    "bilirubin": "Liver",
    "albumin": "Liver",
    "wbc": "Hematology",
    "rbc": "Hematology",
    "platelet": "Hematology",
    "hematocrit": "Hematology",
    "sodium": "Electrolyte",
    "potassium": "Electrolyte",
    "chloride": "Electrolyte",
    "calcium": "Electrolyte",
    "magnesium": "Electrolyte",
    "tsh": "Thyroid",
    "t3": "Thyroid",
    "t4": "Thyroid",
    "troponin": "Cardiac",
    "bnp": "Cardiac",
    "ck": "Cardiac",
    "psa": "Oncology",
    "cea": "Oncology",
    "inr": "Coagulation",
    "ptt": "Coagulation",
    "pt": "Coagulation",
    "urinalysis": "Urinalysis",
    "culture": "Microbiology",
    "covid": "Infectious Disease",
    "hiv": "Infectious Disease",
    "hepatitis": "Infectious Disease",
}


def _build_category_expression():
    """Build a PySpark WHEN chain for test categorization."""
    expr = F.lit("Other")
    for pattern, category in TEST_CATEGORIES.items():
        expr = F.when(
            F.lower(F.col("test_name")).contains(pattern), F.lit(category)
        ).otherwise(expr)
    return expr


def build_lab_analytics(spark) -> None:
    """Build the lab analytics gold table.

    Joins lab results with patient demographics, computes abnormal flags
    based on normal range comparisons, and assigns test categories.
    """
    labs = spark.table(BRONZE_LAB_RESULTS)
    patients = spark.table(BRONZE_PATIENTS)

    # Join lab results with patient demographics
    lab_enriched = labs.join(
        patients.select(
            "patient_id",
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
        ),
        on="patient_id",
        how="inner",
    )

    # Compute age at test
    lab_enriched = lab_enriched.withColumn(
        "age_at_test",
        F.when(
            F.col("date_of_birth").isNotNull() & F.col("test_date").isNotNull(),
            F.floor(F.datediff(F.col("test_date"), F.col("date_of_birth")) / 365.25),
        ).otherwise(F.lit(None)),
    )

    # Compute abnormal flag by comparing result to normal range
    lab_enriched = lab_enriched.withColumn(
        "result_numeric",
        F.regexp_extract(F.col("result_value").cast("string"), r"([\d.]+)", 1).cast(
            "double"
        ),
    )

    lab_enriched = lab_enriched.withColumn(
        "abnormal_flag",
        F.when(
            F.col("result_numeric").isNull(),
            F.lit("UNKNOWN"),
        )
        .when(
            F.col("normal_range_low").isNotNull()
            & (F.col("result_numeric") < F.col("normal_range_low")),
            F.lit("LOW"),
        )
        .when(
            F.col("normal_range_high").isNotNull()
            & (F.col("result_numeric") > F.col("normal_range_high")),
            F.lit("HIGH"),
        )
        .when(
            F.col("normal_range_low").isNotNull()
            | F.col("normal_range_high").isNotNull(),
            F.lit("NORMAL"),
        )
        .otherwise(F.lit("UNKNOWN")),
    )

    # Assign test category
    lab_enriched = lab_enriched.withColumn(
        "test_category", _build_category_expression()
    )

    # Compute critical flag for severely abnormal results
    lab_enriched = lab_enriched.withColumn(
        "is_critical",
        F.when(
            F.col("normal_range_low").isNotNull()
            & F.col("normal_range_high").isNotNull()
            & F.col("result_numeric").isNotNull(),
            (
                F.col("result_numeric")
                < (F.col("normal_range_low") * 0.5)
            )
            | (
                F.col("result_numeric")
                > (F.col("normal_range_high") * 2.0)
            ),
        ).otherwise(F.lit(False)),
    )

    # Select final columns
    result = lab_enriched.select(
        "lab_result_id",
        "patient_id",
        "encounter_id",
        "first_name",
        "last_name",
        "gender",
        "age_at_test",
        "test_name",
        "test_category",
        "test_date",
        "result_value",
        "result_numeric",
        "result_unit",
        "normal_range_low",
        "normal_range_high",
        "abnormal_flag",
        "is_critical",
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

    # Unity Catalog metadata
    try:
        set_table_comment(
            spark,
            FULL_TABLE,
            "Enriched lab test results with patient demographics, abnormal flags, "
            "critical indicators, and test categorization.",
        )
        set_table_tags(
            spark,
            FULL_TABLE,
            {
                "domain": "clinical",
                "layer": "gold",
                "contains_phi": "true",
                "owner": "clinical-data-team",
                "refresh_cadence": "daily",
            },
        )
    except Exception as e:
        print(f"[WARN] Could not set UC metadata: {e}")


def main() -> None:
    """Entry point for the lab analytics curation pipeline."""
    spark = get_spark_session("GoldCuration_LabAnalytics")

    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception as e:
        print(f"[WARN] Could not create schema via UC: {e}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")

    build_lab_analytics(spark)
    spark.stop()


if __name__ == "__main__":
    main()
