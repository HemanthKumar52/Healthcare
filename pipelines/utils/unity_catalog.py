"""Unity Catalog metadata helper functions.

Provides utilities for managing Unity Catalog objects such as catalogs,
schemas, table tags, and table comments via Spark SQL.
"""

from typing import Dict

from pyspark.sql import SparkSession


def create_catalog_if_not_exists(spark: SparkSession, name: str) -> None:
    """Create a Unity Catalog catalog if it does not already exist.

    Args:
        spark: Active SparkSession.
        name: Name of the catalog to create.
    """
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {name}")
    print(f"[UC] Catalog '{name}' ensured.")


def create_schema_if_not_exists(
    spark: SparkSession, catalog: str, schema: str
) -> None:
    """Create a Unity Catalog schema (database) if it does not already exist.

    Args:
        spark: Active SparkSession.
        catalog: Parent catalog name.
        schema: Schema name to create.
    """
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
    print(f"[UC] Schema '{catalog}.{schema}' ensured.")


def set_table_tags(
    spark: SparkSession, table: str, tags_dict: Dict[str, str]
) -> None:
    """Set tags on a Unity Catalog table.

    Tags are key-value pairs stored as metadata on the table. Existing tags
    with the same keys will be overwritten.

    Args:
        spark: Active SparkSession.
        table: Fully qualified table name (catalog.schema.table).
        tags_dict: Dictionary of tag key-value pairs.
    """
    if not tags_dict:
        return

    tag_pairs = ", ".join(
        f"'{key}' = '{value}'" for key, value in tags_dict.items()
    )
    spark.sql(f"ALTER TABLE {table} SET TAGS ({tag_pairs})")
    print(f"[UC] Tags set on '{table}': {tags_dict}")


def set_table_comment(spark: SparkSession, table: str, comment: str) -> None:
    """Set a descriptive comment on a Unity Catalog table.

    Args:
        spark: Active SparkSession.
        table: Fully qualified table name (catalog.schema.table).
        comment: Description text for the table.
    """
    escaped_comment = comment.replace("'", "\\'")
    spark.sql(f"COMMENT ON TABLE {table} IS '{escaped_comment}'")
    print(f"[UC] Comment set on '{table}'.")


def grant_select(spark: SparkSession, table: str, principal: str) -> None:
    """Grant SELECT access on a table to a principal.

    Args:
        spark: Active SparkSession.
        table: Fully qualified table name.
        principal: User or group to grant access to.
    """
    spark.sql(f"GRANT SELECT ON TABLE {table} TO `{principal}`")
    print(f"[UC] SELECT granted on '{table}' to '{principal}'.")


def revoke_select(spark: SparkSession, table: str, principal: str) -> None:
    """Revoke SELECT access on a table from a principal.

    Args:
        spark: Active SparkSession.
        table: Fully qualified table name.
        principal: User or group to revoke access from.
    """
    spark.sql(f"REVOKE SELECT ON TABLE {table} FROM `{principal}`")
    print(f"[UC] SELECT revoked on '{table}' from '{principal}'.")
