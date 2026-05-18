"""Gold layer curation: Patient Visit Summary.

Joins bronze patients, encounters, diagnoses, and procedures into a
comprehensive patient visit summary table in the clinical domain.

Output: healthcare_marketplace.clinical.patient_visit_summary
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
SCHEMA = "clinical"
TABLE = "patient_visit_summary"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"

BRONZE_PATIENTS = f"{CATALOG}.bronze.raw_patients"
BRONZE_ENCOUNTERS = f"{CATALOG}.bronze.raw_encounters"
BRONZE_DIAGNOSES = f"{CATALOG}.bronze.raw_diagnoses"
BRONZE_PROCEDURES = f"{CATALOG}.bronze.raw_procedures"


def build_patient_visit_summary(spark) -> None:
    """Build the patient visit summary gold table.

    Joins patients with encounters, diagnoses, and procedures. Computes
    derived columns such as length of stay, age at visit, and primary
    diagnosis. Filters out records with null required fields.
    """
    patients = spark.table(BRONZE_PATIENTS)
    encounters = spark.table(BRONZE_ENCOUNTERS)
    diagnoses = spark.table(BRONZE_DIAGNOSES)
    procedures = spark.table(BRONZE_PROCEDURES)

    # Determine the primary diagnosis per encounter (first by sequence or earliest)
    diag_window = Window.partitionBy("encounter_id").orderBy(
        F.col("diagnosis_date").asc_nulls_last()
    )
    primary_diagnoses = (
        diagnoses.withColumn("diag_rank", F.row_number().over(diag_window))
        .filter(F.col("diag_rank") == 1)
        .select(
            F.col("encounter_id").alias("diag_encounter_id"),
            F.col("diagnosis_code").alias("primary_diagnosis_code"),
            F.col("diagnosis_description").alias("primary_diagnosis_description"),
        )
    )

    # Count diagnoses and procedures per encounter
    diag_counts = (
        diagnoses.groupBy("encounter_id")
        .agg(
            F.count("*").alias("diagnosis_count"),
            F.collect_set("diagnosis_code").alias("all_diagnosis_codes"),
        )
        .withColumnRenamed("encounter_id", "dc_encounter_id")
    )

    proc_counts = (
        procedures.groupBy("encounter_id")
        .agg(
            F.count("*").alias("procedure_count"),
            F.collect_set("procedure_code").alias("all_procedure_codes"),
        )
        .withColumnRenamed("encounter_id", "pc_encounter_id")
    )

    # Join encounters with patients
    visits = encounters.join(
        patients,
        encounters["patient_id"] == patients["patient_id"],
        "inner",
    ).select(
        encounters["encounter_id"],
        encounters["patient_id"],
        patients["first_name"],
        patients["last_name"],
        patients["gender"],
        patients["date_of_birth"],
        encounters["encounter_date"],
        encounters["discharge_date"],
        encounters["encounter_type"],
        encounters["department_id"],
        encounters["doctor_id"],
    )

    # Add primary diagnosis
    visits = visits.join(
        primary_diagnoses,
        visits["encounter_id"] == primary_diagnoses["diag_encounter_id"],
        "left",
    ).drop("diag_encounter_id")

    # Add diagnosis counts
    visits = visits.join(
        diag_counts,
        visits["encounter_id"] == diag_counts["dc_encounter_id"],
        "left",
    ).drop("dc_encounter_id")

    # Add procedure counts
    visits = visits.join(
        proc_counts,
        visits["encounter_id"] == proc_counts["pc_encounter_id"],
        "left",
    ).drop("pc_encounter_id")

    # Compute derived columns
    visits = visits.withColumn(
        "length_of_stay_days",
        F.when(
            F.col("discharge_date").isNotNull() & F.col("encounter_date").isNotNull(),
            F.datediff(F.col("discharge_date"), F.col("encounter_date")),
        ).otherwise(F.lit(None)),
    )

    visits = visits.withColumn(
        "age_at_visit",
        F.when(
            F.col("date_of_birth").isNotNull() & F.col("encounter_date").isNotNull(),
            F.floor(
                F.datediff(F.col("encounter_date"), F.col("date_of_birth")) / 365.25
            ),
        ).otherwise(F.lit(None)),
    )

    # Fill nulls for counts
    visits = visits.fillna({"diagnosis_count": 0, "procedure_count": 0})

    # Add readmission flag: same patient with encounter within 30 days
    readmit_window = Window.partitionBy("patient_id").orderBy("encounter_date")
    visits = visits.withColumn(
        "prev_discharge_date",
        F.lag("discharge_date").over(readmit_window),
    ).withColumn(
        "is_readmission",
        F.when(
            F.col("prev_discharge_date").isNotNull()
            & (
                F.datediff(F.col("encounter_date"), F.col("prev_discharge_date"))
                <= 30
            ),
            F.lit(True),
        ).otherwise(F.lit(False)),
    ).drop("prev_discharge_date")

    # Filter out records with null required fields
    visits = visits.filter(
        F.col("encounter_id").isNotNull()
        & F.col("patient_id").isNotNull()
        & F.col("encounter_date").isNotNull()
    )

    # Add processing metadata
    visits = visits.withColumn("_processed_at", F.current_timestamp())

    # Write gold table
    (
        visits.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(FULL_TABLE)
    )

    row_count = spark.table(FULL_TABLE).count()
    print(f"[DONE] {FULL_TABLE}: {row_count:,} rows written")

    # Set Unity Catalog metadata
    try:
        set_table_comment(
            spark,
            FULL_TABLE,
            "Aggregated view of patient encounters with diagnoses, procedures, "
            "and derived metrics including length of stay and readmission flags.",
        )
        set_table_tags(
            spark,
            FULL_TABLE,
            {
                "domain": "clinical",
                "layer": "gold",
                "contains_phi": "true",
                "hipaa_certified": "true",
                "owner": "clinical-data-team",
                "refresh_cadence": "daily",
            },
        )
    except Exception as e:
        print(f"[WARN] Could not set UC metadata: {e}")


def main() -> None:
    """Entry point for the patient visit summary curation pipeline."""
    spark = get_spark_session("GoldCuration_PatientVisitSummary")

    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception as e:
        print(f"[WARN] Could not create schema via UC: {e}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")

    build_patient_visit_summary(spark)
    spark.stop()


if __name__ == "__main__":
    main()
