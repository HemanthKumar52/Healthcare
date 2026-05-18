"""Data quality check: Completeness.

Measures the percentage of non-null values across specified columns
in a PySpark DataFrame.
"""

from typing import List

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def check_completeness(df: DataFrame, columns: List[str]) -> float:
    """Check the completeness of specified columns in a DataFrame.

    Completeness is defined as the average non-null rate across all
    specified columns. A score of 1.0 means every value in every
    specified column is non-null. Empty strings are also treated as
    missing values.

    Args:
        df: Input DataFrame to check.
        columns: List of column names to evaluate for completeness.

    Returns:
        A float between 0.0 and 1.0 representing the completeness score.
        Returns 1.0 if the DataFrame is empty or no columns are specified.
    """
    if not columns:
        return 1.0

    # Filter to only columns that exist in the DataFrame
    existing_columns = [c for c in columns if c in df.columns]
    if not existing_columns:
        return 1.0

    total_rows = df.count()
    if total_rows == 0:
        return 1.0

    # Count non-null and non-empty values for each column
    non_null_exprs = [
        F.count(
            F.when(F.col(c).isNotNull() & (F.col(c).cast("string") != ""), c)
        ).alias(c)
        for c in existing_columns
    ]
    non_null_counts = df.select(*non_null_exprs).collect()[0]

    # Average completeness across all specified columns
    per_column_scores = [non_null_counts[c] / total_rows for c in existing_columns]
    score = sum(per_column_scores) / len(per_column_scores)

    return round(score, 6)
