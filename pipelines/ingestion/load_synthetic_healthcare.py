"""Bronze layer ingestion: load synthetic healthcare CSVs into Delta tables.

Reads all 15 CSV files from data/raw/synthetic_healthcare/ and writes them
as Delta tables in the healthcare_marketplace.bronze schema. Each CSV file
becomes a separate table named raw_{filename_without_extension}.
"""

import os
import sys
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DateType, TimestampType

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.spark_session import get_spark_session
from utils.unity_catalog import (
    create_catalog_if_not_exists,
    create_schema_if_not_exists,
    set_table_comment,
    set_table_tags,
)

# Mapping of CSV filenames (without extension) to their table descriptions
CSV_TABLE_MAP = {
    "patients": "Raw patient demographics and personal information",
    "encounters": "Raw clinical encounter/visit records",
    "diagnoses": "Raw diagnosis records with ICD codes",
    "procedures": "Raw procedure records with CPT/HCPCS codes",
    "prescriptions": "Raw medication prescription records",
    "lab_results": "Raw laboratory test results",
    "vitals": "Raw patient vital sign measurements",
    "appointments": "Raw appointment scheduling records",
    "admissions": "Raw hospital admission and discharge records",
    "rooms_beds": "Raw hospital room and bed inventory",
    "departments": "Raw hospital department information",
    "billing": "Raw billing and charge records",
    "insurance_claims": "Raw insurance claim submissions and adjudications",
    "payments": "Raw payment transaction records",
    "doctors": "Raw physician and provider information",
}

# Columns likely to contain dates, mapped per table for parsing
DATE_COLUMNS = {
    "patients": ["date_of_birth", "registration_date"],
    "encounters": ["encounter_date", "discharge_date"],
    "diagnoses": ["diagnosis_date"],
    "procedures": ["procedure_date"],
    "prescriptions": ["prescription_date", "start_date", "end_date"],
    "lab_results": ["test_date", "result_date"],
    "vitals": ["measurement_date", "recorded_at"],
    "appointments": ["appointment_date", "created_date"],
    "admissions": ["admission_date", "discharge_date"],
    "rooms_beds": [],
    "departments": [],
    "billing": ["billing_date", "service_date", "due_date"],
    "insurance_claims": ["claim_date", "submitted_date", "adjudication_date"],
    "payments": ["payment_date"],
    "doctors": ["hire_date"],
}


def find_data_directory() -> str:
    """Locate the synthetic healthcare data directory.

    Searches relative to the script location and common project roots.

    Returns:
        Absolute path to the synthetic healthcare data directory.

    Raises:
        FileNotFoundError: If the data directory cannot be found.
    """
    candidates = [
        Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "synthetic_healthcare",
        Path.cwd() / "data" / "raw" / "synthetic_healthcare",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return str(candidate)
    raise FileNotFoundError(
        "Cannot find data/raw/synthetic_healthcare/ directory. "
        "Searched: " + ", ".join(str(c) for c in candidates)
    )


def parse_date_columns(df: "pyspark.sql.DataFrame", table_name: str) -> "pyspark.sql.DataFrame":
    """Attempt to parse known date columns from string to DateType.

    Only parses columns that actually exist in the DataFrame and contain
    string data. Columns that fail parsing are left as-is.

    Args:
        df: Input DataFrame with string date columns.
        table_name: Name of the table (used to look up known date columns).

    Returns:
        DataFrame with date columns parsed where possible.
    """
    date_cols = DATE_COLUMNS.get(table_name, [])
    existing_cols = set(df.columns)

    for col_name in date_cols:
        if col_name not in existing_cols:
            continue

        # Try multiple date formats
        df = df.withColumn(
            col_name,
            F.coalesce(
                F.to_timestamp(F.col(col_name), "yyyy-MM-dd HH:mm:ss"),
                F.to_timestamp(F.col(col_name), "yyyy-MM-dd'T'HH:mm:ss"),
                F.to_timestamp(F.col(col_name), "MM/dd/yyyy HH:mm:ss"),
                F.to_date(F.col(col_name), "yyyy-MM-dd"),
                F.to_date(F.col(col_name), "MM/dd/yyyy"),
                F.to_date(F.col(col_name), "dd/MM/yyyy"),
            ),
        )

    return df


def load_csv_to_bronze(
    spark: SparkSession,
    data_dir: str,
    catalog: str,
    schema: str,
) -> None:
    """Load all CSV files into bronze Delta tables.

    Args:
        spark: Active SparkSession.
        data_dir: Path to the directory containing CSV files.
        catalog: Unity Catalog catalog name.
        schema: Schema name for bronze tables.
    """
    csv_files = sorted(Path(data_dir).glob("*.csv"))

    if not csv_files:
        print(f"[WARN] No CSV files found in {data_dir}")
        return

    print(f"[INFO] Found {len(csv_files)} CSV files in {data_dir}")
    print("=" * 70)

    total_rows = 0

    for csv_path in csv_files:
        table_name = csv_path.stem.lower()
        full_table_name = f"{catalog}.{schema}.raw_{table_name}"

        print(f"\n[LOAD] Processing: {csv_path.name} -> {full_table_name}")

        # Read CSV with schema inference and header
        df = (
            spark.read.format("csv")
            .option("header", "true")
            .option("inferSchema", "true")
            .option("multiLine", "true")
            .option("escape", '"')
            .option("mode", "PERMISSIVE")
            .load(str(csv_path))
        )

        # Clean column names: lowercase, replace spaces/special chars with underscores
        for col_name in df.columns:
            clean_name = (
                col_name.strip()
                .lower()
                .replace(" ", "_")
                .replace("-", "_")
                .replace(".", "_")
            )
            if clean_name != col_name:
                df = df.withColumnRenamed(col_name, clean_name)

        # Parse date columns
        df = parse_date_columns(df, table_name)

        # Add ingestion metadata
        df = df.withColumn("_ingested_at", F.current_timestamp())
        df = df.withColumn("_source_file", F.lit(csv_path.name))

        # Write as Delta table (overwrite for idempotency)
        (
            df.write.format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(full_table_name)
        )

        row_count = df.count()
        total_rows += row_count
        col_count = len(df.columns)
        description = CSV_TABLE_MAP.get(table_name, f"Raw {table_name} data")

        print(f"       Rows: {row_count:,} | Columns: {col_count} | {description}")

        # Set Unity Catalog metadata
        try:
            set_table_comment(spark, full_table_name, description)
            set_table_tags(
                spark,
                full_table_name,
                {
                    "layer": "bronze",
                    "source": "synthetic_healthcare",
                    "format": "csv",
                    "pipeline": "load_synthetic_healthcare",
                },
            )
        except Exception as e:
            # Tags/comments may fail in local mode without full UC support
            print(f"       [WARN] Could not set UC metadata: {e}")

    print("\n" + "=" * 70)
    print(f"[DONE] Loaded {len(csv_files)} tables with {total_rows:,} total rows")
    print(f"       Catalog: {catalog} | Schema: {schema}")


def main() -> None:
    """Entry point for the synthetic healthcare data ingestion pipeline."""
    spark = get_spark_session("BronzeIngestion_SyntheticHealthcare")

    catalog = "healthcare_marketplace"
    schema = "bronze"

    # Create catalog and schema (may fail in local mode)
    try:
        create_catalog_if_not_exists(spark, catalog)
        create_schema_if_not_exists(spark, catalog, schema)
    except Exception as e:
        print(f"[WARN] Could not create catalog/schema via UC (local mode?): {e}")
        # In local mode, create the database directly
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {schema}")
        catalog = ""  # Use default catalog in local mode

    if not catalog:
        # Local mode fallback: use just schema.table naming
        catalog = "spark_catalog"
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {schema}")

    data_dir = find_data_directory()
    load_csv_to_bronze(spark, data_dir, catalog, schema)

    spark.stop()


if __name__ == "__main__":
    main()
