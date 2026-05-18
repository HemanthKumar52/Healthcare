"""Gold layer curation: CDC Mortality Analysis.

Analyzes CDC WONDER mortality data to produce population-level
mortality trends, leading causes of death, and demographic breakdowns.

Output: healthcare_marketplace.research.cdc_mortality_analysis
"""

import sys
from pathlib import Path

from pyspark.sql import functions as F
from pyspark.sql.window import Window

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from utils.spark_session import get_spark_session
from utils.unity_catalog import (
    create_schema_if_not_exists,
    set_table_comment,
    set_table_tags,
)

CATALOG = "healthcare_marketplace"
SCHEMA = "research"
TABLE = "cdc_mortality_analysis"
FULL_TABLE = f"{CATALOG}.{SCHEMA}.{TABLE}"


def build_cdc_mortality_analysis(spark) -> None:
    """Build CDC mortality analysis gold table.

    Aggregates mortality data by state, year, cause, and demographics
    to produce trend analysis, leading cause rankings, and disparity metrics.
    """
    mortality = spark.table(f"{CATALOG}.bronze.cdc_wonder_mortality")

    # ── State-Year-Cause Summary ────────────────────────────
    state_year_cause = (
        mortality.groupBy("state", "state_code", "year", "cause_category", "cause_of_death_code")
        .agg(
            F.sum("deaths").alias("total_deaths"),
            F.sum("population").alias("total_population"),
        )
        .withColumn("mortality_rate_per_100k",
            F.when(F.col("total_population") > 0,
                F.round(F.col("total_deaths") / F.col("total_population") * 100000, 2)
            ).otherwise(0))
    )

    # ── Rank causes per state-year ──────────────────────────
    w = Window.partitionBy("state", "year").orderBy(F.desc("total_deaths"))
    state_year_cause = state_year_cause.withColumn("cause_rank", F.row_number().over(w))

    # ── Year-over-Year Change ───────────────────────────────
    w_prev = Window.partitionBy("state", "cause_category").orderBy("year")
    state_year_cause = state_year_cause.withColumn(
        "prev_year_deaths", F.lag("total_deaths").over(w_prev)
    ).withColumn("yoy_change_pct",
        F.when(
            F.col("prev_year_deaths").isNotNull() & (F.col("prev_year_deaths") > 0),
            F.round((F.col("total_deaths") - F.col("prev_year_deaths")) / F.col("prev_year_deaths") * 100, 2)
        ).otherwise(None)
    )

    # ── Demographic Breakdown (by gender and race) ──────────
    demo_summary = (
        mortality.groupBy("state", "year", "cause_category", "gender", "race")
        .agg(
            F.sum("deaths").alias("deaths"),
            F.sum("population").alias("population"),
        )
        .withColumn("rate_per_100k",
            F.when(F.col("population") > 0,
                F.round(F.col("deaths") / F.col("population") * 100000, 2)
            ).otherwise(0))
    )

    # ── Gender Disparity Ratio ──────────────────────────────
    gender_rates = (
        demo_summary.groupBy("state", "year", "cause_category", "gender")
        .agg(F.sum("deaths").alias("deaths"), F.sum("population").alias("population"))
        .withColumn("rate", F.col("deaths") / F.col("population") * 100000)
    )
    male_rates = gender_rates.filter(F.col("gender") == "Male").select(
        F.col("state").alias("m_state"), F.col("year").alias("m_year"),
        F.col("cause_category").alias("m_cause"), F.col("rate").alias("male_rate"),
    )
    female_rates = gender_rates.filter(F.col("gender") == "Female").select(
        F.col("state").alias("f_state"), F.col("year").alias("f_year"),
        F.col("cause_category").alias("f_cause"), F.col("rate").alias("female_rate"),
    )
    gender_disparity = male_rates.join(
        female_rates,
        (male_rates["m_state"] == female_rates["f_state"]) &
        (male_rates["m_year"] == female_rates["f_year"]) &
        (male_rates["m_cause"] == female_rates["f_cause"]),
        "inner",
    ).withColumn("gender_disparity_ratio",
        F.when(F.col("female_rate") > 0,
            F.round(F.col("male_rate") / F.col("female_rate"), 2)
        ).otherwise(None)
    ).select("m_state", "m_year", "m_cause", "male_rate", "female_rate", "gender_disparity_ratio")

    # ── Final Table: Join state_year_cause with gender disparity ─
    result = state_year_cause.join(
        gender_disparity,
        (state_year_cause["state"] == gender_disparity["m_state"]) &
        (state_year_cause["year"] == gender_disparity["m_year"]) &
        (state_year_cause["cause_category"] == gender_disparity["m_cause"]),
        "left",
    ).drop("m_state", "m_year", "m_cause", "prev_year_deaths")

    result = result.withColumn("_processed_at", F.current_timestamp())

    result = result.select(
        "state", "state_code", "year", "cause_category", "cause_of_death_code",
        "total_deaths", "total_population", "mortality_rate_per_100k",
        "cause_rank", "yoy_change_pct",
        "male_rate", "female_rate", "gender_disparity_ratio",
        "_processed_at",
    )

    (
        result.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(FULL_TABLE)
    )

    row_count = spark.table(FULL_TABLE).count()
    print(f"[DONE] {FULL_TABLE}: {row_count:,} rows written")

    # Print national leading causes for latest year
    print("\n  National Leading Causes (latest year):")
    latest = (
        spark.table(FULL_TABLE)
        .filter(F.col("year") == spark.table(FULL_TABLE).agg(F.max("year")).collect()[0][0])
        .groupBy("cause_category")
        .agg(F.sum("total_deaths").alias("deaths"))
        .orderBy(F.desc("deaths"))
        .limit(10)
        .collect()
    )
    for i, row in enumerate(latest, 1):
        print(f"    {i:>2}. {row['cause_category']:>30}: {row['deaths']:>10,}")

    try:
        set_table_comment(spark, FULL_TABLE,
            "CDC WONDER mortality trend analysis with state-level cause rankings, "
            "year-over-year changes, and gender disparity ratios.")
        set_table_tags(spark, FULL_TABLE, {
            "domain": "research", "layer": "gold", "source": "cdc_wonder",
            "contains_phi": "false", "owner": "research-data-team", "refresh_cadence": "monthly",
        })
    except Exception as e:
        print(f"  [WARN] Could not set UC metadata: {e}")


def main() -> None:
    spark = get_spark_session("GoldCuration_CDCMortalityAnalysis")
    try:
        create_schema_if_not_exists(spark, CATALOG, SCHEMA)
    except Exception:
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {SCHEMA}")
    build_cdc_mortality_analysis(spark)
    spark.stop()


if __name__ == "__main__":
    main()
