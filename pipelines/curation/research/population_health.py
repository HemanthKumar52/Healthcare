"""Gold layer curation: Population Health.

Reads bronze patients and diagnoses, applies de-identification, and
produces aggregated population health statistics by age group, gender,
and diagnosis prevalence.

Output: healthcare_marketplace.research.population_health
"""

import sys
from pathlib import Path

from pyspark.sql import functions as F

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from utils.deidentification import (
    generalize_age,
    hash_column,
    remove_phi_columns,
)
from utils.spark_session import get_spark_session
from utils.unity_catalog import (
    create_schema_if_not_exists,
    set_table_comment,
    set_table_tags,
)

CATALOG = "healthcare_marketplace"
SCHEMA = "research"
TABLE = "population_health"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"

BRONZE_PATIENTS = f"{CATALOG}.bronze.raw_patients"
BRONZE_DIAGNOSES = f"{CATALOG}.bronze.raw_diagnoses"

# PHI columns that must never appear in research tables
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
    "zip_code",
    "postal_code",
    "date_of_birth",
    "mrn",
    "medical_record_number",
    "insurance_id",
    "insurance_number",
    "_source_file",
]


def build_population_health(spark) -> None:
    """Build the de-identified population health gold table.

    Joins patients with diagnoses, removes all PHI, generalizes ages
    into buckets, hashes patient IDs, and aggregates health metrics
    by demographic groups.
    """
    patients = spark.table(BRONZE_PATIENTS)
    diagnoses = spark.table(BRONZE_DIAGNOSES)

    # Compute age from date of birth before removing it
    patients_with_age = patients.withColumn(
        "age",
        F.when(
            F.col("date_of_birth").isNotNull(),
            F.floor(
                F.datediff(F.current_date(), F.col("date_of_birth")) / 365.25
            ),
        ).otherwise(F.lit(None)),
    )

    # Remove PHI columns
    patients_deidentified = remove_phi_columns(patients_with_age, PHI_COLUMNS)

    # Hash patient_id for pseudonymization
    patients_deidentified = hash_column(patients_deidentified, "patient_id")

    # Generalize age into 5-year buckets
    patients_deidentified = generalize_age(patients_deidentified, "age", bucket_size=5)
    patients_deidentified = patients_deidentified.withColumnRenamed("age", "age_group")

    # Prepare diagnoses: hash patient_id to match
    diagnoses_deidentified = hash_column(diagnoses, "patient_id")
    diagnoses_deidentified = remove_phi_columns(
        diagnoses_deidentified, ["_source_file"]
    )

    # Count diagnoses per patient
    patient_diagnosis_counts = (
        diagnoses_deidentified.groupBy("patient_id")
        .agg(
            F.countDistinct("diagnosis_code").alias("unique_diagnosis_count"),
            F.count("*").alias("total_diagnosis_count"),
        )
        .withColumnRenamed("patient_id", "diag_patient_id")
    )

    # Join patients with diagnosis counts
    patient_summary = patients_deidentified.join(
        patient_diagnosis_counts,
        patients_deidentified["patient_id"]
        == patient_diagnosis_counts["diag_patient_id"],
        "left",
    ).drop("diag_patient_id")

    patient_summary = patient_summary.fillna(
        {"unique_diagnosis_count": 0, "total_diagnosis_count": 0}
    )

    # Aggregate by age_group and gender for population-level stats
    population_stats = (
        patient_summary.groupBy("age_group", "gender")
        .agg(
            F.count("*").alias("patient_count"),
            F.avg("unique_diagnosis_count").alias("avg_diagnoses_per_patient"),
            F.max("unique_diagnosis_count").alias("max_diagnoses_per_patient"),
        )
    )

    # Compute diagnosis prevalence: top diagnoses by age_group and gender
    diagnosis_prevalence = (
        diagnoses_deidentified.join(
            patients_deidentified.select("patient_id", "age_group", "gender"),
            on="patient_id",
            how="inner",
        )
        .groupBy("age_group", "gender", "diagnosis_code", "diagnosis_description")
        .agg(
            F.countDistinct("patient_id").alias("affected_patients"),
            F.count("*").alias("total_occurrences"),
        )
    )

    # Write population statistics table
    population_stats = population_stats.withColumn(
        "_processed_at", F.current_timestamp()
    )
    (
        population_stats.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(FULL_TABLE)
    )

    # Write diagnosis prevalence as a supplementary table
    prevalence_table = f"{CATALOG}.{SCHEMA}.diagnosis_prevalence"
    (
        diagnosis_prevalence.withColumn("_processed_at", F.current_timestamp())
        .write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(prevalence_table)
    )

    pop_count = spark.table(FULL_TABLE).count()
    prev_count = spark.table(prevalence_table).count()
    print(f"[DONE] {FULL_TABLE}: {pop_count:,} rows written")
    print(f"[DONE] {prevalence_table}: {prev_count:,} rows written")

    # Unity Catalog metadata
    try:
        set_table_comment(
            spark,
            FULL_TABLE,
            "De-identified population health statistics aggregated by age group "
            "and gender. All PHI removed per Safe Harbor methodology.",
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
                "owner": "research-data-team",
                "refresh_cadence": "weekly",
            },
        )
    except Exception as e:
        print(f"[WARN] Could not set UC metadata: {e}")


def main() -> None:
    """Entry point for the population health curation pipeline."""
    spark = get_spark_session("GoldCuration_PopulationHealth")

    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception as e:
        print(f"[WARN] Could not create schema via UC: {e}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")

    build_population_health(spark)
    spark.stop()


if __name__ == "__main__":
    main()
