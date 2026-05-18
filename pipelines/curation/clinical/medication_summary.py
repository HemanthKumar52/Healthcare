"""Gold layer curation: Medication Summary.

Joins bronze prescriptions with patients and doctors to produce a
medication summary with prescription counts and prescribing details.

Output: healthcare_marketplace.clinical.medication_summary
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
TABLE = "medication_summary"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"

BRONZE_PRESCRIPTIONS = f"{CATALOG}.bronze.raw_prescriptions"
BRONZE_PATIENTS = f"{CATALOG}.bronze.raw_patients"
BRONZE_DOCTORS = f"{CATALOG}.bronze.raw_doctors"


def build_medication_summary(spark) -> None:
    """Build the medication summary gold table.

    Enriches prescriptions with patient demographics and prescribing
    doctor information. Computes per-patient prescription counts,
    medication duration, and identifies top prescribed medications.
    """
    prescriptions = spark.table(BRONZE_PRESCRIPTIONS)
    patients = spark.table(BRONZE_PATIENTS)
    doctors = spark.table(BRONZE_DOCTORS)

    # Join prescriptions with patient demographics
    enriched = prescriptions.join(
        patients.select(
            F.col("patient_id").alias("pat_id"),
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
        ),
        prescriptions["patient_id"] == F.col("pat_id"),
        "inner",
    ).drop("pat_id")

    # Join with prescribing doctor
    enriched = enriched.join(
        doctors.select(
            F.col("doctor_id").alias("doc_id"),
            F.col("first_name").alias("doctor_first_name"),
            F.col("last_name").alias("doctor_last_name"),
            F.col("specialty").alias("doctor_specialty"),
            F.col("department_id").alias("doctor_department_id"),
        ),
        enriched["doctor_id"] == F.col("doc_id"),
        "left",
    ).drop("doc_id")

    # Compute medication duration in days
    enriched = enriched.withColumn(
        "medication_duration_days",
        F.when(
            F.col("start_date").isNotNull() & F.col("end_date").isNotNull(),
            F.datediff(F.col("end_date"), F.col("start_date")),
        ).otherwise(F.lit(None)),
    )

    # Compute age at prescription
    enriched = enriched.withColumn(
        "age_at_prescription",
        F.when(
            F.col("date_of_birth").isNotNull()
            & F.col("prescription_date").isNotNull(),
            F.floor(
                F.datediff(F.col("prescription_date"), F.col("date_of_birth"))
                / 365.25
            ),
        ).otherwise(F.lit(None)),
    )

    # Compute per-patient prescription count (running total)
    patient_window = Window.partitionBy("patient_id").orderBy("prescription_date")
    enriched = enriched.withColumn(
        "patient_prescription_seq",
        F.row_number().over(patient_window),
    )

    # Total prescriptions per patient
    patient_totals = (
        prescriptions.groupBy("patient_id")
        .agg(
            F.count("*").alias("total_patient_prescriptions"),
            F.countDistinct("medication_name").alias("unique_medications_per_patient"),
        )
        .withColumnRenamed("patient_id", "pt_id")
    )

    enriched = enriched.join(
        patient_totals,
        enriched["patient_id"] == patient_totals["pt_id"],
        "left",
    ).drop("pt_id")

    # Rank medications by overall prescription frequency
    med_popularity = (
        prescriptions.groupBy("medication_name")
        .agg(F.count("*").alias("global_prescription_count"))
    )
    med_window = Window.orderBy(F.col("global_prescription_count").desc())
    med_popularity = med_popularity.withColumn(
        "medication_popularity_rank", F.row_number().over(med_window)
    ).select("medication_name", "global_prescription_count", "medication_popularity_rank")

    enriched = enriched.join(
        med_popularity.withColumnRenamed("medication_name", "med_name"),
        enriched["medication_name"] == F.col("med_name"),
        "left",
    ).drop("med_name")

    # Determine if medication is currently active
    enriched = enriched.withColumn(
        "is_active",
        F.when(
            F.col("end_date").isNull()
            | (F.col("end_date") >= F.current_date()),
            F.lit(True),
        ).otherwise(F.lit(False)),
    )

    # Select final columns
    result = enriched.select(
        "prescription_id",
        "patient_id",
        "encounter_id",
        "first_name",
        "last_name",
        "gender",
        "age_at_prescription",
        "medication_name",
        "dosage",
        "frequency",
        "prescription_date",
        "start_date",
        "end_date",
        "medication_duration_days",
        "is_active",
        "doctor_id",
        "doctor_first_name",
        "doctor_last_name",
        "doctor_specialty",
        "patient_prescription_seq",
        "total_patient_prescriptions",
        "unique_medications_per_patient",
        "global_prescription_count",
        "medication_popularity_rank",
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
            "Prescription records enriched with patient demographics, prescribing "
            "doctor details, medication duration, and popularity ranking.",
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
    """Entry point for the medication summary curation pipeline."""
    spark = get_spark_session("GoldCuration_MedicationSummary")

    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception as e:
        print(f"[WARN] Could not create schema via UC: {e}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")

    build_medication_summary(spark)
    spark.stop()


if __name__ == "__main__":
    main()
