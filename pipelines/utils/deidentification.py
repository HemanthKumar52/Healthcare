"""De-identification utilities for healthcare data.

Provides functions to de-identify Protected Health Information (PHI) in
PySpark DataFrames, following Safe Harbor methodology principles.
"""

from typing import List

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType


def hash_column(df: DataFrame, col_name: str) -> DataFrame:
    """Replace a column's values with their SHA-256 hash.

    Useful for creating pseudonymous identifiers that are consistent
    (same input always produces the same hash) but not reversible.

    Args:
        df: Input DataFrame.
        col_name: Name of the column to hash.

    Returns:
        DataFrame with the specified column replaced by its SHA-256 hash.
    """
    return df.withColumn(col_name, F.sha2(F.col(col_name).cast("string"), 256))


def mask_column(
    df: DataFrame,
    col_name: str,
    mask_char: str = "*",
    visible_chars: int = 2,
) -> DataFrame:
    """Mask a column's values, leaving only the last N characters visible.

    For example, with visible_chars=2 and mask_char='*', the value
    "John Smith" becomes "********th".

    Args:
        df: Input DataFrame.
        col_name: Name of the column to mask.
        mask_char: Character used for masking.
        visible_chars: Number of trailing characters to leave visible.

    Returns:
        DataFrame with the specified column masked.
    """
    return df.withColumn(
        col_name,
        F.when(
            F.col(col_name).isNull(),
            F.lit(None),
        ).otherwise(
            F.concat(
                F.expr(
                    f"repeat('{mask_char}', greatest(length({col_name}) - {visible_chars}, 0))"
                ),
                F.expr(
                    f"right({col_name}, least(length({col_name}), {visible_chars}))"
                ),
            )
        ),
    )


def generalize_age(
    df: DataFrame, col_name: str, bucket_size: int = 5
) -> DataFrame:
    """Replace exact ages with age-range buckets.

    For example, with bucket_size=5, age 37 becomes "35-39".
    Ages 90 and above are grouped into a single "90+" bucket per
    Safe Harbor de-identification guidelines.

    Args:
        df: Input DataFrame.
        col_name: Name of the age column.
        bucket_size: Width of each age bucket.

    Returns:
        DataFrame with the age column replaced by age-range strings.
    """
    bucket_lower = (F.col(col_name).cast(IntegerType()) / bucket_size).cast(
        IntegerType()
    ) * bucket_size
    bucket_upper = bucket_lower + (bucket_size - 1)

    return df.withColumn(
        col_name,
        F.when(F.col(col_name).isNull(), F.lit(None))
        .when(
            F.col(col_name).cast(IntegerType()) >= 90,
            F.lit("90+"),
        )
        .otherwise(
            F.concat(
                bucket_lower.cast("string"),
                F.lit("-"),
                bucket_upper.cast("string"),
            )
        ),
    )


def remove_phi_columns(df: DataFrame, phi_columns_list: List[str]) -> DataFrame:
    """Drop columns that contain Protected Health Information.

    Only drops columns that actually exist in the DataFrame; missing
    column names are silently ignored.

    Args:
        df: Input DataFrame.
        phi_columns_list: List of column names to remove.

    Returns:
        DataFrame with PHI columns removed.
    """
    existing_columns = set(df.columns)
    columns_to_drop = [c for c in phi_columns_list if c in existing_columns]
    if columns_to_drop:
        df = df.drop(*columns_to_drop)
    return df


def shift_dates(
    df: DataFrame, date_columns: List[str], shift_days: int = -30
) -> DataFrame:
    """Shift date columns by a fixed number of days.

    Preserves temporal relationships between dates within a record while
    obscuring the actual calendar dates.

    Args:
        df: Input DataFrame.
        date_columns: List of date column names to shift.
        shift_days: Number of days to add (negative to shift earlier).

    Returns:
        DataFrame with shifted date columns.
    """
    for col_name in date_columns:
        if col_name in df.columns:
            df = df.withColumn(
                col_name,
                F.date_add(F.col(col_name), shift_days),
            )
    return df


def generalize_zip_code(df: DataFrame, col_name: str) -> DataFrame:
    """Truncate zip codes to the first 3 digits for de-identification.

    Per Safe Harbor, zip codes with populations under 20,000 based on
    the first 3 digits should be set to "000". This function truncates
    to 3 digits as a baseline; population-based suppression should be
    applied separately if needed.

    Args:
        df: Input DataFrame.
        col_name: Name of the zip code column.

    Returns:
        DataFrame with generalized zip codes.
    """
    return df.withColumn(
        col_name,
        F.when(
            F.col(col_name).isNull(),
            F.lit(None),
        ).otherwise(
            F.concat(F.substring(F.col(col_name).cast("string"), 1, 3), F.lit("00"))
        ),
    )
