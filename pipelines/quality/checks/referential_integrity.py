"""Data quality check: Referential Integrity.

Measures the percentage of foreign key values that exist in a
reference table, validating relationships between datasets.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def check_referential_integrity(
    df: DataFrame, col: str, reference_df: DataFrame, ref_col: str
) -> float:
    """Check referential integrity between a column and a reference table.

    Computes the percentage of non-null values in the specified column
    that have a matching value in the reference column of the reference
    DataFrame.

    Args:
        df: Source DataFrame containing the foreign key column.
        col: Name of the foreign key column in the source DataFrame.
        reference_df: Reference DataFrame containing the primary key.
        ref_col: Name of the primary key column in the reference DataFrame.

    Returns:
        A float between 0.0 and 1.0 representing the referential integrity
        score. Returns 1.0 if the source column has no non-null values.
        Returns 0.0 if either column doesn't exist in its DataFrame.
    """
    if col not in df.columns or ref_col not in reference_df.columns:
        return 0.0

    # Only check non-null values in the source column
    non_null_df = df.filter(F.col(col).isNotNull())
    total = non_null_df.count()

    if total == 0:
        return 1.0

    # Get distinct reference values for efficient lookup
    ref_values = reference_df.select(
        F.col(ref_col).alias("_ref_key")
    ).distinct()

    # Inner join to count matches
    matched = (
        non_null_df.join(
            ref_values, non_null_df[col] == ref_values["_ref_key"], "inner"
        ).count()
    )

    score = matched / total
    return round(score, 6)
