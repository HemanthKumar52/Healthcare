"""Spark session factory for Healthcare Data Marketplace pipelines.

Creates a SparkSession configured for local development with Delta Lake
or for Databricks with Unity Catalog, depending on the runtime environment.
"""

import os
from pyspark.sql import SparkSession


def get_spark_session(app_name: str = "HealthcareDataMarketplace") -> SparkSession:
    """Create and return a configured SparkSession.

    If the DATABRICKS_RUNTIME_VERSION environment variable is set, the session
    is created without a master URL (Databricks manages the cluster). Otherwise,
    a local session is created with Delta Lake extensions enabled.

    Args:
        app_name: Name for the Spark application.

    Returns:
        A configured SparkSession instance.
    """
    is_databricks = os.environ.get("DATABRICKS_RUNTIME_VERSION") is not None

    builder = SparkSession.builder.appName(app_name)

    if is_databricks:
        # On Databricks, Delta Lake and Unity Catalog are pre-configured.
        # Enable Unity Catalog as the default catalog provider.
        builder = builder.config(
            "spark.sql.catalog.spark_catalog",
            "com.databricks.sql.transaction.tahoe.catalog.DeltaCatalog",
        )
    else:
        # Local development: configure master and Delta Lake extensions.
        builder = (
            builder.master("local[*]")
            .config(
                "spark.sql.extensions",
                "io.delta.sql.DeltaSparkSessionExtension",
            )
            .config(
                "spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog",
            )
            .config("spark.sql.warehouse.dir", "/tmp/healthcare_marketplace/warehouse")
            .config("spark.driver.memory", "4g")
            .config("spark.sql.shuffle.partitions", "8")
        )

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark
