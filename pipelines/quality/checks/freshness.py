"""Data quality check: Freshness.

Measures how recently data was updated based on a timestamp column,
scoring against a maximum acceptable age threshold.
"""

from datetime import datetime, timezone
from typing import Union

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def check_freshness(
    df: DataFrame, timestamp_col: str, max_age_hours: Union[int, float] = 24
) -> float:
    """Check the freshness of data based on the most recent timestamp.

    Freshness is scored as a ratio between 0.0 and 1.0:
    - 1.0 if the most recent record is within the max_age_hours window
    - Degrades linearly from 1.0 to 0.0 as age exceeds max_age_hours,
      reaching 0.0 at 3x the max age

    Args:
        df: Input DataFrame to check.
        timestamp_col: Name of the timestamp or date column to evaluate.
        max_age_hours: Maximum acceptable age in hours for a perfect score.

    Returns:
        A float between 0.0 and 1.0 representing the freshness score.
        Returns 0.0 if the column doesn't exist, the DataFrame is empty,
        or no valid timestamps are found.
    """
    if timestamp_col not in df.columns:
        return 0.0

    if max_age_hours <= 0:
        return 0.0

    # Get the most recent timestamp
    result = df.agg(F.max(F.col(timestamp_col)).alias("latest")).collect()[0]
    latest = result["latest"]

    if latest is None:
        return 0.0

    # Handle string timestamps
    if isinstance(latest, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                latest = datetime.strptime(latest, fmt)
                break
            except ValueError:
                continue

    # Calculate age in hours
    now = datetime.now()
    if hasattr(latest, "tzinfo") and latest.tzinfo is not None:
        now = datetime.now(timezone.utc)

    age_hours = (now - latest).total_seconds() / 3600

    if age_hours <= max_age_hours:
        return 1.0

    # Linear degradation from 1.0 to 0.0 over the range
    # [max_age_hours, 3 * max_age_hours]
    max_tolerable = max_age_hours * 3
    if age_hours >= max_tolerable:
        return 0.0

    score = 1.0 - (age_hours - max_age_hours) / (max_tolerable - max_age_hours)
    return round(score, 6)
