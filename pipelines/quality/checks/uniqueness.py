"""Data quality check: Uniqueness.

Measures the percentage of unique (non-duplicate) value combinations
across specified columns in a PySpark DataFrame.
"""

from typing import List

from pyspark.sql import DataFrame


def check_uniqueness(df: DataFrame, columns: List[str]) -> float:
    """Check the uniqueness of specified columns in a DataFrame.

    Uniqueness is defined as the ratio of distinct value combinations
    to total rows. A score of 1.0 means every row has a unique
    combination of values in the specified columns (no duplicates).

    For a single column like a primary key, a score of 1.0 confirms
    no duplicate keys exist. For composite columns, uniqueness is
    evaluated on the combination.

    Args:
        df: Input DataFrame to check.
        columns: List of column names to evaluate for uniqueness as a
            composite key.

    Returns:
        A float between 0.0 and 1.0 representing the uniqueness score.
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

    distinct_count = df.select(existing_columns).distinct().count()
    score = distinct_count / total_rows

    return round(score, 6)
