"""Quality Engine: Run quality checks based on data product YAML configuration.

Takes a product configuration YAML path as argument, runs all defined quality
checks (completeness, uniqueness, freshness, value_range, referential_integrity),
and outputs scores to console. Optionally writes results to a quality_scores
Delta table.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quality.checks.completeness import check_completeness
from quality.checks.freshness import check_freshness
from quality.checks.referential_integrity import check_referential_integrity
from quality.checks.uniqueness import check_uniqueness
from quality.checks.value_range import check_value_range
from utils.spark_session import get_spark_session

QUALITY_SCORES_TABLE = "marketplace_metadata.quality.quality_scores"


def load_config(config_path: str) -> Dict[str, Any]:
    """Load and parse a YAML configuration file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Parsed YAML content as a dictionary.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_quality_checks(product_config: Dict[str, Any], write_results: bool = False) -> Dict[str, Any]:
    """Run all quality checks defined in a product configuration.

    Reads the target table, executes each configured quality check, and
    compiles results into a summary report. Optionally persists scores
    to a Delta table.

    Args:
        product_config: Parsed YAML config dict with product and quality
            check definitions.
        write_results: If True, write quality scores to the quality_scores
            Delta table.

    Returns:
        Dictionary containing individual metric scores, overall score,
        SLA breach information, and metadata.
    """
    spark = get_spark_session("QualityEngine")

    source = product_config["source"]
    table_name = f"{source['catalog']}.{source['schema']}.{source['table']}"
    product_name = product_config["product"]["name"]
    product_slug = product_config["product"].get("slug", product_name.lower().replace(" ", "-"))

    print(f"\n{'=' * 60}")
    print(f"Quality Check: {product_name}")
    print(f"Table: {table_name}")
    print(f"{'=' * 60}")

    try:
        df = spark.table(table_name)
    except Exception as e:
        print(f"[ERROR] Cannot read table {table_name}: {e}")
        return {
            "product_name": product_name,
            "product_slug": product_slug,
            "table": table_name,
            "error": str(e),
            "scores": {},
            "overall_score": 0.0,
            "sla_breaches": [],
            "checked_at": datetime.now().isoformat(),
        }

    row_count = df.count()
    print(f"  Rows: {row_count:,}")

    checks = product_config.get("quality", {}).get("checks", [])
    scores: Dict[str, float] = {}
    check_details: List[Dict[str, Any]] = []

    for check in checks:
        metric = check["metric"]
        threshold = check.get("threshold")

        if metric == "completeness":
            columns = check.get("columns", [])
            score = check_completeness(df, columns)
            scores["completeness"] = score
            detail = f"columns=[{', '.join(columns)}]"

        elif metric == "uniqueness":
            columns = check.get("columns", [])
            score = check_uniqueness(df, columns)
            scores["uniqueness"] = score
            detail = f"columns=[{', '.join(columns)}]"

        elif metric == "freshness":
            timestamp_col = check.get("timestamp_column", check.get("column", "_processed_at"))
            max_age = check.get("max_age_hours", 24)
            score = check_freshness(df, timestamp_col, max_age)
            scores["freshness"] = score
            detail = f"col={timestamp_col}, max_age={max_age}h"

        elif metric == "value_range":
            col = check["column"]
            min_val = check.get("min")
            max_val = check.get("max")
            score = check_value_range(df, col, min_val, max_val)
            scores["value_range"] = score
            detail = f"col={col}, range=[{min_val}, {max_val}]"

        elif metric == "referential_integrity":
            col = check["column"]
            ref_table = check["reference_table"]
            ref_col = check["reference_column"]
            try:
                ref_df = spark.table(ref_table)
                score = check_referential_integrity(df, col, ref_df, ref_col)
            except Exception as e:
                print(f"  [WARN] Cannot load reference table {ref_table}: {e}")
                score = 0.0
            scores["referential_integrity"] = score
            detail = f"{col} -> {ref_table}.{ref_col}"

        else:
            print(f"  [WARN] Unknown metric: {metric}")
            continue

        # Check against threshold
        passed = True
        if threshold is not None:
            passed = score >= threshold

        status = "PASS" if passed else "FAIL"
        print(f"  {metric:>25}: {score:.4f}  (threshold: {threshold})  [{status}]")

        check_details.append({
            "metric": metric,
            "score": score,
            "threshold": threshold,
            "passed": passed,
            "detail": detail,
        })

    # Calculate overall score (average of all checks)
    if scores:
        overall_score = round(sum(scores.values()) / len(scores), 6)
    else:
        overall_score = 1.0

    scores["overall"] = overall_score

    # Identify SLA breaches
    sla_breaches = [
        {
            "metric": d["metric"],
            "score": d["score"],
            "threshold": d["threshold"],
        }
        for d in check_details
        if not d["passed"] and d["threshold"] is not None
    ]

    if sla_breaches:
        print(f"\n  SLA BREACHES ({len(sla_breaches)}):")
        for breach in sla_breaches:
            print(
                f"    {breach['metric']}: {breach['score']:.4f} "
                f"< {breach['threshold']:.4f}"
            )
    else:
        print("\n  All SLAs met.")

    print(f"\n  Overall Quality Score: {overall_score:.4f}")
    print(f"{'=' * 60}\n")

    result = {
        "product_name": product_name,
        "product_slug": product_slug,
        "table": table_name,
        "scores": scores,
        "check_details": check_details,
        "sla_breaches": sla_breaches,
        "row_count": row_count,
        "overall_score": overall_score,
        "checked_at": datetime.now().isoformat(),
    }

    # Optionally write scores to Delta table
    if write_results:
        try:
            _write_quality_scores(spark, result)
        except Exception as e:
            print(f"[WARN] Could not write quality scores: {e}")

    return result


def _write_quality_scores(spark, result: Dict[str, Any]) -> None:
    """Write quality check results to the quality_scores Delta table.

    Args:
        spark: Active SparkSession.
        result: Quality check result dictionary.
    """
    from pyspark.sql import Row
    from pyspark.sql import functions as F

    scores = result["scores"]
    row = Row(
        product_name=result["product_name"],
        product_slug=result["product_slug"],
        table_name=result["table"],
        completeness=scores.get("completeness"),
        uniqueness=scores.get("uniqueness"),
        freshness=scores.get("freshness"),
        referential_integrity=scores.get("referential_integrity"),
        value_range=scores.get("value_range"),
        overall_score=result["overall_score"],
        row_count=result["row_count"],
        sla_breach_count=len(result["sla_breaches"]),
        checked_at=result["checked_at"],
    )

    scores_df = spark.createDataFrame([row])
    scores_df = scores_df.withColumn("_written_at", F.current_timestamp())

    (
        scores_df.write.format("delta")
        .mode("append")
        .saveAsTable(QUALITY_SCORES_TABLE)
    )

    print(f"[INFO] Quality scores written to {QUALITY_SCORES_TABLE}")


def main() -> None:
    """Entry point for the quality engine CLI."""
    parser = argparse.ArgumentParser(
        description="Healthcare Data Marketplace Quality Engine"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to data product YAML configuration file",
    )
    parser.add_argument(
        "--product",
        help="Product name to check (for multi-product config files)",
    )
    parser.add_argument(
        "--write-results",
        action="store_true",
        help="Write quality scores to the quality_scores Delta table",
    )
    parser.add_argument(
        "--output",
        help="Path to write JSON results file",
    )
    args = parser.parse_args()

    config_data = load_config(args.config)

    # Handle multi-product config files (products key contains a list)
    if "products" in config_data:
        products = config_data["products"]
        if args.product:
            products = [
                p for p in products
                if p["product"]["name"] == args.product
                or p["product"].get("slug") == args.product
            ]
            if not products:
                print(f"[ERROR] Product '{args.product}' not found in config")
                sys.exit(1)
    else:
        # Single product config
        products = [config_data]

    all_results = []
    for product_config in products:
        result = run_quality_checks(product_config, write_results=args.write_results)
        all_results.append(result)

    # Print summary
    if len(all_results) > 1:
        print("\n" + "=" * 60)
        print("QUALITY SUMMARY")
        print("=" * 60)
        for r in all_results:
            breach_text = f" ({len(r['sla_breaches'])} breaches)" if r["sla_breaches"] else ""
            print(f"  {r['product_name']:>30}: {r['overall_score']:.4f}{breach_text}")
        print("=" * 60)

    # Write JSON output if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\nResults written to: {output_path}")


if __name__ == "__main__":
    main()
