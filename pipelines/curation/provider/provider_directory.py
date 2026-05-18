"""Gold layer curation: Provider Directory.

Reads bronze doctors table and enriches it with patient counts and
aggregated metrics to create a comprehensive provider directory.

Output: healthcare_marketplace.provider.provider_directory
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
SCHEMA = "provider"
TABLE = "provider_directory"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"

BRONZE_DOCTORS = f"{CATALOG}.bronze.raw_doctors"
BRONZE_ENCOUNTERS = f"{CATALOG}.bronze.raw_encounters"
BRONZE_APPOINTMENTS = f"{CATALOG}.bronze.raw_appointments"
BRONZE_DEPARTMENTS = f"{CATALOG}.bronze.raw_departments"


def build_provider_directory(spark) -> None:
    """Build the provider directory gold table.

    Enriches doctor records with patient counts, encounter volumes,
    appointment statistics, and department information.
    """
    doctors = spark.table(BRONZE_DOCTORS)

    # Try to load related tables for enrichment
    try:
        encounters = spark.table(BRONZE_ENCOUNTERS)
        has_encounters = True
    except Exception:
        has_encounters = False

    try:
        appointments = spark.table(BRONZE_APPOINTMENTS)
        has_appointments = True
    except Exception:
        has_appointments = False

    try:
        departments = spark.table(BRONZE_DEPARTMENTS)
        has_departments = True
    except Exception:
        has_departments = False

    result = doctors

    # Enrich with encounter-based metrics
    if has_encounters:
        encounter_stats = (
            encounters.groupBy("doctor_id")
            .agg(
                F.countDistinct("patient_id").alias("unique_patient_count"),
                F.count("*").alias("total_encounters"),
                F.min("encounter_date").alias("first_encounter_date"),
                F.max("encounter_date").alias("last_encounter_date"),
                F.countDistinct("encounter_type").alias("encounter_type_count"),
            )
            .withColumnRenamed("doctor_id", "enc_doctor_id")
        )
        result = result.join(
            encounter_stats,
            result["doctor_id"] == encounter_stats["enc_doctor_id"],
            "left",
        ).drop("enc_doctor_id")
    else:
        result = (
            result.withColumn("unique_patient_count", F.lit(None).cast("long"))
            .withColumn("total_encounters", F.lit(None).cast("long"))
            .withColumn("first_encounter_date", F.lit(None).cast("date"))
            .withColumn("last_encounter_date", F.lit(None).cast("date"))
            .withColumn("encounter_type_count", F.lit(None).cast("long"))
        )

    # Enrich with appointment-based metrics
    if has_appointments:
        appt_stats = (
            appointments.groupBy("doctor_id")
            .agg(
                F.count("*").alias("total_appointments"),
                F.avg(
                    F.when(
                        F.lower(F.col("status")).isin(
                            "no_show", "no-show", "noshow", "missed"
                        ),
                        F.lit(1),
                    ).otherwise(F.lit(0))
                ).alias("no_show_rate"),
                F.avg(
                    F.when(
                        F.lower(F.col("status")).isin("completed", "done"),
                        F.lit(1),
                    ).otherwise(F.lit(0))
                ).alias("completion_rate"),
            )
            .withColumnRenamed("doctor_id", "appt_doctor_id")
        )
        result = result.join(
            appt_stats,
            result["doctor_id"] == appt_stats["appt_doctor_id"],
            "left",
        ).drop("appt_doctor_id")
    else:
        result = (
            result.withColumn("total_appointments", F.lit(None).cast("long"))
            .withColumn("no_show_rate", F.lit(None).cast("double"))
            .withColumn("completion_rate", F.lit(None).cast("double"))
        )

    # Enrich with department name
    if has_departments:
        result = result.join(
            departments.select(
                F.col("department_id").alias("dept_id"),
                F.col("department_name"),
            ),
            result["department_id"] == F.col("dept_id"),
            "left",
        ).drop("dept_id")
    else:
        result = result.withColumn("department_name", F.lit(None).cast("string"))

    # Compute years of service
    result = result.withColumn(
        "years_of_service",
        F.when(
            F.col("hire_date").isNotNull(),
            F.round(
                F.datediff(F.current_date(), F.col("hire_date")) / 365.25, 1
            ),
        ).otherwise(F.lit(None)),
    )

    # Compute provider display name
    result = result.withColumn(
        "provider_display_name",
        F.concat(
            F.lit("Dr. "),
            F.col("first_name"),
            F.lit(" "),
            F.col("last_name"),
        ),
    )

    # Determine active status
    result = result.withColumn(
        "is_active",
        F.when(
            F.col("last_encounter_date").isNotNull()
            & (
                F.datediff(F.current_date(), F.col("last_encounter_date")) <= 365
            ),
            F.lit(True),
        ).when(
            F.col("last_encounter_date").isNull(),
            F.lit(True),  # Assume active if no encounters yet
        ).otherwise(F.lit(False)),
    )

    # Round rates
    result = result.withColumn(
        "no_show_rate", F.round(F.col("no_show_rate"), 4)
    ).withColumn(
        "completion_rate", F.round(F.col("completion_rate"), 4)
    )

    # Fill nulls for count columns
    result = result.fillna(
        {
            "unique_patient_count": 0,
            "total_encounters": 0,
            "total_appointments": 0,
        }
    )

    # Select final columns
    result = result.select(
        "doctor_id",
        "provider_display_name",
        "first_name",
        "last_name",
        "specialty",
        "department_id",
        "department_name",
        "hire_date",
        "years_of_service",
        "is_active",
        "unique_patient_count",
        "total_encounters",
        "total_appointments",
        "no_show_rate",
        "completion_rate",
        "first_encounter_date",
        "last_encounter_date",
        "encounter_type_count",
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
            "Enriched provider directory with patient counts, encounter volumes, "
            "appointment statistics, and years of service.",
        )
        set_table_tags(
            spark,
            FULL_TABLE,
            {
                "domain": "provider",
                "layer": "gold",
                "contains_phi": "false",
                "owner": "provider-data-team",
                "refresh_cadence": "weekly",
            },
        )
    except Exception as e:
        print(f"[WARN] Could not set UC metadata: {e}")


def main() -> None:
    """Entry point for the provider directory curation pipeline."""
    spark = get_spark_session("GoldCuration_ProviderDirectory")

    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception as e:
        print(f"[WARN] Could not create schema via UC: {e}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")

    build_provider_directory(spark)
    spark.stop()


if __name__ == "__main__":
    main()
