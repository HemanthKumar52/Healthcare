"""Gold layer curation: Appointment Analytics.

Joins bronze appointments with doctors and departments to produce
scheduling analytics with no-show rates and utilization metrics.

Output: healthcare_marketplace.operational.appointment_analytics
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
SCHEMA = "operational"
TABLE = "appointment_analytics"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"

BRONZE_APPOINTMENTS = f"{CATALOG}.bronze.raw_appointments"
BRONZE_DOCTORS = f"{CATALOG}.bronze.raw_doctors"
BRONZE_DEPARTMENTS = f"{CATALOG}.bronze.raw_departments"


def build_appointment_analytics(spark) -> None:
    """Build the appointment analytics gold table.

    Computes no-show rates, average wait times, appointments per doctor,
    and identifies the busiest hours and days of the week.
    """
    appointments = spark.table(BRONZE_APPOINTMENTS)
    doctors = spark.table(BRONZE_DOCTORS)
    departments = spark.table(BRONZE_DEPARTMENTS)

    # Extract time-based features from appointment date
    appts = appointments.withColumn(
        "appointment_hour",
        F.hour(F.col("appointment_date")),
    ).withColumn(
        "appointment_day_of_week",
        F.dayofweek(F.col("appointment_date")),
    ).withColumn(
        "appointment_month",
        F.month(F.col("appointment_date")),
    ).withColumn(
        "appointment_year",
        F.year(F.col("appointment_date")),
    )

    # Flag no-shows
    appts = appts.withColumn(
        "is_no_show",
        F.when(
            F.lower(F.col("status")).isin("no_show", "no-show", "noshow", "missed"),
            F.lit(True),
        ).otherwise(F.lit(False)),
    )

    # Flag cancellations
    appts = appts.withColumn(
        "is_cancelled",
        F.when(
            F.lower(F.col("status")).isin("cancelled", "canceled"),
            F.lit(True),
        ).otherwise(F.lit(False)),
    )

    # Flag completed
    appts = appts.withColumn(
        "is_completed",
        F.when(
            F.lower(F.col("status")).isin("completed", "done", "finished"),
            F.lit(True),
        ).otherwise(F.lit(False)),
    )

    # Per-doctor metrics
    doctor_metrics = (
        appts.groupBy("doctor_id")
        .agg(
            F.count("*").alias("total_appointments"),
            F.sum(F.col("is_no_show").cast("int")).alias("no_show_count"),
            F.sum(F.col("is_cancelled").cast("int")).alias("cancelled_count"),
            F.sum(F.col("is_completed").cast("int")).alias("completed_count"),
        )
        .withColumn(
            "no_show_rate",
            F.when(
                F.col("total_appointments") > 0,
                F.round(F.col("no_show_count") / F.col("total_appointments"), 4),
            ).otherwise(F.lit(0.0)),
        )
        .withColumn(
            "cancellation_rate",
            F.when(
                F.col("total_appointments") > 0,
                F.round(F.col("cancelled_count") / F.col("total_appointments"), 4),
            ).otherwise(F.lit(0.0)),
        )
        .withColumn(
            "completion_rate",
            F.when(
                F.col("total_appointments") > 0,
                F.round(F.col("completed_count") / F.col("total_appointments"), 4),
            ).otherwise(F.lit(0.0)),
        )
    )

    # Join with doctor details
    doctor_metrics = doctor_metrics.join(
        doctors.select(
            F.col("doctor_id").alias("doc_id"),
            F.col("first_name").alias("doctor_first_name"),
            F.col("last_name").alias("doctor_last_name"),
            F.col("specialty").alias("doctor_specialty"),
            "department_id",
        ),
        doctor_metrics["doctor_id"] == F.col("doc_id"),
        "left",
    ).drop("doc_id")

    # Join with department details
    doctor_metrics = doctor_metrics.join(
        departments.select(
            F.col("department_id").alias("dept_id"),
            F.col("department_name"),
        ),
        doctor_metrics["department_id"] == F.col("dept_id"),
        "left",
    ).drop("dept_id")

    # Hourly distribution (busiest hours)
    hourly_stats = (
        appts.groupBy("appointment_hour")
        .agg(
            F.count("*").alias("appointments_in_hour"),
            F.avg(F.col("is_no_show").cast("int")).alias("hourly_no_show_rate"),
        )
    )

    # Rank doctors by appointment volume
    rank_window = Window.orderBy(F.col("total_appointments").desc())
    doctor_metrics = doctor_metrics.withColumn(
        "doctor_volume_rank", F.row_number().over(rank_window)
    )

    # Select final columns for doctor-level analytics
    result = doctor_metrics.select(
        "doctor_id",
        "doctor_first_name",
        "doctor_last_name",
        "doctor_specialty",
        "department_id",
        "department_name",
        "total_appointments",
        "completed_count",
        "no_show_count",
        "cancelled_count",
        "no_show_rate",
        "cancellation_rate",
        "completion_rate",
        "doctor_volume_rank",
        F.current_timestamp().alias("_processed_at"),
    )

    # Write gold table
    (
        result.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(FULL_TABLE)
    )

    # Write hourly distribution as a supplementary table
    hourly_table = f"{CATALOG}.{SCHEMA}.appointment_hourly_distribution"
    (
        hourly_stats.withColumn("_processed_at", F.current_timestamp())
        .write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(hourly_table)
    )

    row_count = spark.table(FULL_TABLE).count()
    print(f"[DONE] {FULL_TABLE}: {row_count:,} rows written")
    print(f"[DONE] {hourly_table}: {hourly_stats.count():,} rows written")

    # Unity Catalog metadata
    try:
        set_table_comment(
            spark,
            FULL_TABLE,
            "Doctor-level appointment analytics including no-show rates, "
            "cancellation rates, and volume rankings by department.",
        )
        set_table_tags(
            spark,
            FULL_TABLE,
            {
                "domain": "operational",
                "layer": "gold",
                "contains_phi": "false",
                "owner": "operations-team",
                "refresh_cadence": "daily",
            },
        )
    except Exception as e:
        print(f"[WARN] Could not set UC metadata: {e}")


def main() -> None:
    """Entry point for the appointment analytics curation pipeline."""
    spark = get_spark_session("GoldCuration_AppointmentAnalytics")

    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception as e:
        print(f"[WARN] Could not create schema via UC: {e}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")

    build_appointment_analytics(spark)
    spark.stop()


if __name__ == "__main__":
    main()
