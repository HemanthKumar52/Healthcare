"""Bronze layer ingestion: load CMS DE-SynPUF CSVs into Delta tables.

Reads CMS beneficiary summary, inpatient claims, outpatient claims, and
prescription drug event CSVs from data/datasets/ and writes them as
Delta tables in the healthcare_marketplace.bronze schema.
"""

import sys
from pathlib import Path

from pyspark.sql import functions as F
from pyspark.sql.types import FloatType, IntegerType

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

CMS_FILES = {
    "cms_beneficiary_summary": {
        "file": "cms_beneficiary_summary.csv",
        "description": "CMS DE-SynPUF beneficiary summary with demographics, chronic conditions, and cost data",
        "date_columns": ["BENE_BIRTH_DT", "BENE_DEATH_DT"],
    },
    "cms_inpatient_claims": {
        "file": "cms_inpatient_claims.csv",
        "description": "CMS DE-SynPUF inpatient claims with diagnoses, procedures, and payment amounts",
        "date_columns": ["CLM_FROM_DT", "CLM_THRU_DT", "CLM_ADMSN_DT", "NCH_BENE_DSCHRG_DT"],
    },
    "cms_outpatient_claims": {
        "file": "cms_outpatient_claims.csv",
        "description": "CMS DE-SynPUF outpatient claims with services, diagnoses, and costs",
        "date_columns": ["CLM_FROM_DT", "CLM_THRU_DT"],
    },
    "cms_prescription_events": {
        "file": "cms_prescription_events.csv",
        "description": "CMS DE-SynPUF prescription drug events with NDC codes, quantities, and costs",
        "date_columns": ["SRVC_DT"],
    },
}


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


def parse_cms_dates(df, date_columns: list[str]):
    """Parse CMS-style date strings (YYYYMMDD) to date type."""
    for col_name in date_columns:
        if col_name in df.columns:
            df = df.withColumn(
                col_name,
                F.when(
                    (F.col(col_name).isNotNull()) & (F.col(col_name) != ""),
                    F.to_date(F.col(col_name), "yyyyMMdd")
                ).otherwise(None)
            )
    return df


def main() -> None:
    """Load all CMS DE-SynPUF CSV files into bronze Delta tables."""
    spark = get_spark_session("BronzeIngestion_CMS")
    data_dir = find_data_directory()

    try:
        create_catalog_if_not_exists(spark, CATALOG)
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception as e:
        print(f"[WARN] Could not create catalog/schema via UC: {e}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")

    print(f"\nLoading CMS DE-SynPUF data from: {data_dir}\n")

    for table_name, config in CMS_FILES.items():
        csv_path = str(Path(data_dir) / config["file"])
        full_table = f"{CATALOG}.{SCHEMA}.{table_name}"

        if not Path(csv_path).exists():
            print(f"[SKIP] {config['file']} not found")
            continue

        print(f"Loading {config['file']}...")

        df = (
            spark.read.format("csv")
            .option("header", "true")
            .option("inferSchema", "true")
            .load(csv_path)
        )

        # Parse date columns
        df = parse_cms_dates(df, config["date_columns"])

        # Add ingestion metadata
        df = df.withColumn("_source_file", F.lit(config["file"]))
        df = df.withColumn("_ingested_at", F.current_timestamp())

        # Write to Delta
        (
            df.write.format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(full_table)
        )

        row_count = spark.table(full_table).count()
        col_count = len(spark.table(full_table).columns)
        print(f"  [DONE] {full_table}: {row_count:,} rows, {col_count} columns")

        # Set UC metadata
        try:
            set_table_comment(spark, full_table, config["description"])
            set_table_tags(spark, full_table, {
                "source": "cms_de_synpuf",
                "layer": "bronze",
                "domain": "financial",
                "contains_phi": "false",
            })
        except Exception as e:
            print(f"  [WARN] Could not set UC metadata: {e}")

    print("\nCMS DE-SynPUF ingestion complete.")
    spark.stop()


if __name__ == "__main__":
    main()
