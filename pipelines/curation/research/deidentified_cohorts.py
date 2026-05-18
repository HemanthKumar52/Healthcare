"""Gold layer curation: De-identified Cohorts.

Creates research-ready patient cohorts from patients, encounters, and
lab results with full de-identification applied.

Output: healthcare_marketplace.research.deidentified_cohorts
"""

import sys
from pathlib import Path

from pyspark.sql import functions as F
from pyspark.sql.window import Window

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from utils.deidentification import (
    generalize_age,
    generalize_zip_code,
    hash_column,
    remove_phi_columns,
    shift_dates,
)
from utils.spark_session import get_spark_session
from utils.unity_catalog import (
    create_schema_if_not_exists,
    set_table_comment,
    set_table_tags,
)

CATALOG = "healthcare_marketplace"
SCHEMA = "research"
TABLE = "deidentified_cohorts"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"

BRONZE_PATIENTS = f"{CATALOG}.bronze.raw_patients"
BRONZE_ENCOUNTERS = f"{CATALOG}.bronze.raw_encounters"
BRONZE_LAB_RESULTS = f"{CATALOG}.bronze.raw_lab_results"
BRONZE_DIAGNOSES = f"{CATALOG}.bronze.raw_diagnoses"

PHI_COLUMNS = [
    "first_name",
    "last_name",
    "ssn",
    "social_security_number",
    "address",
    "street_address",
    "phone",
    "phone_number",
    "email",
    "email_address",
    "date_of_birth",
    "mrn",
    "medical_record_number",
    "insurance_id",
    "insurance_number",
    "_source_file",
    "_ingested_at",
]


def build_deidentified_cohorts(spark) -> None:
    """Build the de-identified research cohorts gold table.

    Joins patients with encounters, lab results, and diagnoses, then
    applies comprehensive de-identification including hashing, date
    shifting, age generalization, and PHI removal.
    """
    patients = spark.table(BRONZE_PATIENTS)
    encounters = spark.table(BRONZE_ENCOUNTERS)
    lab_results = spark.table(BRONZE_LAB_RESULTS)
    diagnoses = spark.table(BRONZE_DIAGNOSES)

    # Compute age before removing date_of_birth
    patients = patients.withColumn(
        "age",
        F.when(
            F.col("date_of_birth").isNotNull(),
            F.floor(
                F.datediff(F.current_date(), F.col("date_of_birth")) / 365.25
            ),
        ).otherwise(F.lit(None)),
    )

    # Aggregate encounter metrics per patient
    encounter_summary = (
        encounters.groupBy("patient_id")
        .agg(
            F.count("*").alias("total_encounters"),
            F.countDistinct("encounter_type").alias("unique_encounter_types"),
            F.min("encounter_date").alias("first_encounter_date"),
            F.max("encounter_date").alias("last_encounter_date"),
            F.avg(
                F.when(
                    F.col("discharge_date").isNotNull()
                    & F.col("encounter_date").isNotNull(),
                    F.datediff(F.col("discharge_date"), F.col("encounter_date")),
                )
            ).alias("avg_length_of_stay"),
        )
        .withColumnRenamed("patient_id", "enc_patient_id")
    )

    # Aggregate lab result metrics per patient
    lab_summary = (
        lab_results.groupBy("patient_id")
        .agg(
            F.count("*").alias("total_lab_tests"),
            F.countDistinct("test_name").alias("unique_lab_tests"),
            F.min("test_date").alias("first_lab_date"),
            F.max("test_date").alias("last_lab_date"),
        )
        .withColumnRenamed("patient_id", "lab_patient_id")
    )

    # Aggregate diagnosis information per patient
    diag_summary = (
        diagnoses.groupBy("patient_id")
        .agg(
            F.countDistinct("diagnosis_code").alias("unique_diagnoses"),
            F.count("*").alias("total_diagnosis_records"),
            F.collect_set("diagnosis_code").alias("diagnosis_codes"),
        )
        .withColumnRenamed("patient_id", "diag_patient_id")
    )

    # Build cohort base from patients
    cohort = patients.select(
        "patient_id",
        "gender",
        "age",
        "zip_code",
        "blood_type",
    )

    # Join with encounter summary
    cohort = cohort.join(
        encounter_summary,
        cohort["patient_id"] == encounter_summary["enc_patient_id"],
        "left",
    ).drop("enc_patient_id")

    # Join with lab summary
    cohort = cohort.join(
        lab_summary,
        cohort["patient_id"] == lab_summary["lab_patient_id"],
        "left",
    ).drop("lab_patient_id")

    # Join with diagnosis summary
    cohort = cohort.join(
        diag_summary,
        cohort["patient_id"] == diag_summary["diag_patient_id"],
        "left",
    ).drop("diag_patient_id")

    # Fill nulls for count columns
    cohort = cohort.fillna(
        {
            "total_encounters": 0,
            "unique_encounter_types": 0,
            "total_lab_tests": 0,
            "unique_lab_tests": 0,
            "unique_diagnoses": 0,
            "total_diagnosis_records": 0,
        }
    )

    # Apply de-identification: hash patient_id
    cohort = hash_column(cohort, "patient_id")

    # Generalize age into 5-year buckets
    cohort = generalize_age(cohort, "age", bucket_size=5)
    cohort = cohort.withColumnRenamed("age", "age_group")

    # Generalize zip code to 3-digit prefix
    if "zip_code" in cohort.columns:
        cohort = generalize_zip_code(cohort, "zip_code")

    # Shift dates by a fixed offset
    date_cols = [
        "first_encounter_date",
        "last_encounter_date",
        "first_lab_date",
        "last_lab_date",
    ]
    cohort = shift_dates(cohort, date_cols, shift_days=-30)

    # Remove any remaining PHI columns
    cohort = remove_phi_columns(cohort, PHI_COLUMNS)

    # Compute comorbidity index (simplified: number of unique diagnoses)
    cohort = cohort.withColumn(
        "comorbidity_index",
        F.when(F.col("unique_diagnoses") == 0, F.lit("None"))
        .when(F.col("unique_diagnoses") <= 2, F.lit("Low"))
        .when(F.col("unique_diagnoses") <= 5, F.lit("Moderate"))
        .otherwise(F.lit("High")),
    )

    # Compute healthcare utilization level
    cohort = cohort.withColumn(
        "utilization_level",
        F.when(F.col("total_encounters") == 0, F.lit("None"))
        .when(F.col("total_encounters") <= 3, F.lit("Low"))
        .when(F.col("total_encounters") <= 10, F.lit("Moderate"))
        .otherwise(F.lit("High")),
    )

    # Add processing metadata
    cohort = cohort.withColumn("_processed_at", F.current_timestamp())

    # Write gold table
    (
        cohort.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(FULL_TABLE)
    )

    row_count = spark.table(FULL_TABLE).count()
    print(f"[DONE] {FULL_TABLE}: {row_count:,} rows written")

    # Print cohort summary
    print("\n  Cohort Summary:")
    summary = (
        spark.table(FULL_TABLE)
        .agg(
            F.count("*").alias("total_patients"),
            F.countDistinct("age_group").alias("age_groups"),
            F.avg("total_encounters").alias("avg_encounters"),
            F.avg("unique_diagnoses").alias("avg_diagnoses"),
        )
        .collect()[0]
    )
    print(f"    Total patients:    {summary['total_patients']:,}")
    print(f"    Age groups:        {summary['age_groups']}")
    print(f"    Avg encounters:    {summary['avg_encounters']:.1f}")
    print(f"    Avg diagnoses:     {summary['avg_diagnoses']:.1f}")

    # Unity Catalog metadata
    try:
        set_table_comment(
            spark,
            FULL_TABLE,
            "De-identified patient cohorts with aggregated encounter, lab, and "
            "diagnosis metrics. All PHI removed and dates shifted per Safe Harbor.",
        )
        set_table_tags(
            spark,
            FULL_TABLE,
            {
                "domain": "research",
                "layer": "gold",
                "contains_phi": "false",
                "deidentified": "true",
                "method": "safe_harbor",
                "date_shift_days": "-30",
                "owner": "research-data-team",
                "refresh_cadence": "weekly",
            },
        )
    except Exception as e:
        print(f"[WARN] Could not set UC metadata: {e}")


def main() -> None:
    """Entry point for the de-identified cohorts curation pipeline."""
    spark = get_spark_session("GoldCuration_DeidentifiedCohorts")

    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception as e:
        print(f"[WARN] Could not create schema via UC: {e}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")

    build_deidentified_cohorts(spark)
    spark.stop()


if __name__ == "__main__":
    main()
