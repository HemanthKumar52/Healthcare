"""Data quality check: Value Range.

Measures the percentage of values in a column that fall within an
expected numeric range.
"""

from typing import Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def check_value_range(
    df: DataFrame,
    col: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> float:
    """Check the percentage of values within an expected range.

    Evaluates a numeric column and returns the fraction of non-null
    values that fall within [min_val, max_val]. If only one bound is
    specified, only that bound is checked.

    Args:
        df: Input DataFrame to check.
        col: Name of the numeric column to evaluate.
        min_val: Minimum acceptable value (inclusive). None means no lower bound.
        max_val: Maximum acceptable value (inclusive). None means no upper bound.

    Returns:
        A float between 0.0 and 1.0 representing the percentage of values
        within the expected range. Returns 1.0 if no bounds are specified
        or if all non-null values are in range. Returns 0.0 if the column
        doesn't exist.
    """
    if col not in df.columns:
        return 0.0

    if min_val is None and max_val is None:
        return 1.0

    # Only evaluate non-null values
    non_null_df = df.filter(F.col(col).isNotNull())
    total = non_null_df.count()

    if total == 0:
        return 1.0

    # Build the in-range condition
    conditions = []
    if min_val is not None:
        conditions.append(F.col(col).cast("double") >= float(min_val))
    if max_val is not None:
        conditions.append(F.col(col).cast("double") <= float(max_val))

    # Combine conditions with AND
    combined_condition = conditions[0]
    for condition in conditions[1:]:
        combined_condition = combined_condition & condition

    in_range_count = non_null_df.filter(combined_condition).count()
    score = in_range_count / total

    return round(score, 6)
