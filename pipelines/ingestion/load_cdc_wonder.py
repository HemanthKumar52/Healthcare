"""Bronze layer ingestion: load CDC WONDER mortality data into Delta tables.

Reads the CDC WONDER tab-delimited mortality export from data/datasets/
and writes it as a Delta table in the healthcare_marketplace.bronze schema.
"""

import sys
from pathlib import Path

from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, FloatType

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.spark_session import get_spark_session
from utils.unity_catalog import (
    create_catalog_if_not_exists,
    create_schema_if_not_exists,
    set_table_comment,
    set_table_tags,
)

CATALOG = "healthcare_marketplace"
SCHEMA = "bronze"
TABLE = "cdc_wonder_mortality"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"


def find_data_directory() -> str:
    """Locate the datasets directory."""
    candidates = [
        Path(__file__).resolve().parent.parent.parent / "data" / "datasets",
        Path.cwd() / "data" / "datasets",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return str(candidate)
    raise FileNotFoundError(
        "Cannot find data/datasets/ directory. "
        "Searched: " + ", ".join(str(c) for c in candidates)
    )


def main() -> None:
    """Load CDC WONDER mortality data into bronze Delta table."""
    spark = get_spark_session("BronzeIngestion_CDC")
    data_dir = find_data_directory()

    try:
        create_catalog_if_not_exists(spark, CATALOG)
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception as e:
        print(f"[WARN] Could not create catalog/schema via UC: {e}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")

    csv_path = str(Path(data_dir) / "cdc_wonder_mortality.csv")

    if not Path(csv_path).exists():
        print(f"[ERROR] cdc_wonder_mortality.csv not found at {csv_path}")
        return

    print(f"\nLoading CDC WONDER mortality data from: {csv_path}\n")

    df = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .option("delimiter", "\t")
        .load(csv_path)
    )

    # Clean column names (replace spaces with underscores)
    for col_name in df.columns:
        clean_name = col_name.strip().replace(" ", "_").replace("(", "").replace(")", "").lower()
        df = df.withColumnRenamed(col_name, clean_name)

    # Cast numeric columns
    numeric_cols = ["deaths", "population", "year", "year_code", "age_group_code", "race_code"]
    for col_name in numeric_cols:
        if col_name in df.columns:
            df = df.withColumn(col_name, F.col(col_name).cast(IntegerType()))

    float_cols = ["crude_rate", "age_adjusted_rate"]
    for col_name in float_cols:
        if col_name in df.columns:
            df = df.withColumn(col_name, F.col(col_name).cast(FloatType()))

    # Add ingestion metadata
    df = df.withColumn("_source_file", F.lit("cdc_wonder_mortality.csv"))
    df = df.withColumn("_ingested_at", F.current_timestamp())

    # Write to Delta
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(FULL_TABLE)
    )

    row_count = spark.table(FULL_TABLE).count()
    col_count = len(spark.table(FULL_TABLE).columns)
    print(f"  [DONE] {FULL_TABLE}: {row_count:,} rows, {col_count} columns")

    # Print summary
    print("\n  Top causes of death:")
    top_causes = (
        spark.table(FULL_TABLE)
        .groupBy("cause_category")
        .agg(F.sum("deaths").alias("total_deaths"))
        .orderBy(F.desc("total_deaths"))
        .limit(10)
        .collect()
    )
    for row in top_causes:
        print(f"    {row['cause_category']:>30}: {row['total_deaths']:>10,} deaths")

    # Set UC metadata
    try:
        set_table_comment(
            spark, FULL_TABLE,
            "CDC WONDER detailed mortality data by state, year, cause of death, "
            "age group, gender, and race with crude and age-adjusted rates."
        )
        set_table_tags(spark, FULL_TABLE, {
            "source": "cdc_wonder",
            "layer": "bronze",
            "domain": "research",
            "contains_phi": "false",
        })
    except Exception as e:
        print(f"  [WARN] Could not set UC metadata: {e}")

    print("\nCDC WONDER ingestion complete.")
    spark.stop()


if __name__ == "__main__":
    main()
