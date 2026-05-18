"""Gold layer curation: Bed Utilization.

Joins bronze admissions, rooms/beds, and departments to produce
bed utilization metrics per department.

Output: healthcare_marketplace.operational.bed_utilization
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
SCHEMA = "operational"
TABLE = "bed_utilization"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"

BRONZE_ADMISSIONS = f"{CATALOG}.bronze.raw_admissions"
BRONZE_ROOMS_BEDS = f"{CATALOG}.bronze.raw_rooms_beds"
BRONZE_DEPARTMENTS = f"{CATALOG}.bronze.raw_departments"


def build_bed_utilization(spark) -> None:
    """Build the bed utilization gold table.

    Computes occupancy rates, average length of stay, and bed turnover
    rates per department by joining admissions with room/bed inventory
    and department metadata.
    """
    admissions = spark.table(BRONZE_ADMISSIONS)
    rooms_beds = spark.table(BRONZE_ROOMS_BEDS)
    departments = spark.table(BRONZE_DEPARTMENTS)

    # Compute length of stay per admission
    admissions_with_los = admissions.withColumn(
        "length_of_stay_days",
        F.when(
            F.col("admission_date").isNotNull() & F.col("discharge_date").isNotNull(),
            F.datediff(F.col("discharge_date"), F.col("admission_date")),
        ).otherwise(F.lit(None)),
    )

    # Determine if admission is currently active (no discharge date)
    admissions_with_los = admissions_with_los.withColumn(
        "is_currently_admitted",
        F.when(F.col("discharge_date").isNull(), F.lit(True)).otherwise(F.lit(False)),
    )

    # Count total beds per department from rooms_beds
    beds_per_dept = (
        rooms_beds.groupBy("department_id")
        .agg(
            F.count("*").alias("total_beds"),
            F.sum(
                F.when(F.col("status") == "available", 1).otherwise(0)
            ).alias("available_beds"),
            F.sum(
                F.when(F.col("status") == "occupied", 1).otherwise(0)
            ).alias("occupied_beds"),
        )
        .withColumnRenamed("department_id", "rb_department_id")
    )

    # Aggregate admission metrics per department
    dept_admission_stats = (
        admissions_with_los.groupBy("department_id")
        .agg(
            F.count("*").alias("total_admissions"),
            F.avg("length_of_stay_days").alias("avg_length_of_stay_days"),
            F.min("length_of_stay_days").alias("min_length_of_stay_days"),
            F.max("length_of_stay_days").alias("max_length_of_stay_days"),
            F.stddev("length_of_stay_days").alias("stddev_length_of_stay_days"),
            F.sum(
                F.when(F.col("is_currently_admitted"), 1).otherwise(0)
            ).alias("current_inpatients"),
            F.countDistinct("patient_id").alias("unique_patients"),
        )
        .withColumnRenamed("department_id", "adm_department_id")
    )

    # Join department info with bed counts and admission stats
    result = departments.join(
        beds_per_dept,
        departments["department_id"] == beds_per_dept["rb_department_id"],
        "left",
    ).drop("rb_department_id")

    result = result.join(
        dept_admission_stats,
        departments["department_id"] == dept_admission_stats["adm_department_id"],
        "left",
    ).drop("adm_department_id")

    # Compute occupancy rate
    result = result.withColumn(
        "occupancy_rate",
        F.when(
            F.col("total_beds").isNotNull() & (F.col("total_beds") > 0),
            F.round(F.col("occupied_beds") / F.col("total_beds"), 4),
        ).otherwise(F.lit(None)),
    )

    # Compute bed turnover rate (admissions per bed in the period)
    result = result.withColumn(
        "bed_turnover_rate",
        F.when(
            F.col("total_beds").isNotNull() & (F.col("total_beds") > 0),
            F.round(F.col("total_admissions") / F.col("total_beds"), 2),
        ).otherwise(F.lit(None)),
    )

    # Compute average daily census (approximation)
    result = result.withColumn(
        "avg_daily_census",
        F.when(
            F.col("avg_length_of_stay_days").isNotNull()
            & F.col("total_admissions").isNotNull(),
            F.round(
                (F.col("total_admissions") * F.col("avg_length_of_stay_days")) / 365,
                1,
            ),
        ).otherwise(F.lit(None)),
    )

    # Select final columns
    result = result.select(
        "department_id",
        "department_name",
        "total_beds",
        "available_beds",
        "occupied_beds",
        "occupancy_rate",
        "total_admissions",
        "unique_patients",
        "current_inpatients",
        "avg_length_of_stay_days",
        "min_length_of_stay_days",
        "max_length_of_stay_days",
        "stddev_length_of_stay_days",
        "bed_turnover_rate",
        "avg_daily_census",
        F.current_timestamp().alias("_processed_at"),
    )

    # Fill nulls for metric columns
    result = result.fillna(
        {
            "total_admissions": 0,
            "unique_patients": 0,
            "current_inpatients": 0,
            "total_beds": 0,
            "available_beds": 0,
            "occupied_beds": 0,
        }
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
            "Department-level bed utilization metrics including occupancy rates, "
            "average length of stay, and bed turnover rates.",
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
    """Entry point for the bed utilization curation pipeline."""
    spark = get_spark_session("GoldCuration_BedUtilization")

    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception as e:
        print(f"[WARN] Could not create schema via UC: {e}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")

    build_bed_utilization(spark)
    spark.stop()


if __name__ == "__main__":
    main()
