"""PHI Scanner: Detect potential Protected Health Information in DataFrames.

Scans PySpark DataFrames for potential PHI using regex pattern matching
on both column names and sampled values. Detects SSNs, MRNs, phone
numbers, email addresses, and common name patterns.
"""

import re
from typing import Any, Dict, List

from pyspark.sql import DataFrame
from pyspark.sql.types import StringType


# Regex patterns for common PHI elements found in values
PHI_VALUE_PATTERNS: Dict[str, str] = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "ssn_no_dash": r"\b\d{9}\b",
    "mrn": r"\b(MRN|mrn|MR)[:\s#]?\d{6,12}\b",
    "phone_us": r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "zip_full": r"\b\d{5}-\d{4}\b",
    "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "date_mdyhms": r"\b\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2}\b",
    "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
}

# Column name patterns that suggest PHI presence
PHI_COLUMN_PATTERNS: List[Dict[str, str]] = [
    {"label": "name", "pattern": r"(?i)(first.?name|last.?name|full.?name|patient.?name|middle.?name)"},
    {"label": "ssn", "pattern": r"(?i)(ssn|social.?security)"},
    {"label": "mrn", "pattern": r"(?i)(mrn|medical.?record)"},
    {"label": "address", "pattern": r"(?i)(address|street|city|zip|postal|state|county)"},
    {"label": "contact", "pattern": r"(?i)(phone|fax|email|e.?mail|mobile|telephone)"},
    {"label": "dob", "pattern": r"(?i)(date.?of.?birth|dob|birth.?date|birthday)"},
    {"label": "insurance", "pattern": r"(?i)(insurance.?id|policy.?number|member.?id|group.?number)"},
    {"label": "license", "pattern": r"(?i)(license|certificate|npi|dea)"},
    {"label": "financial", "pattern": r"(?i)(credit.?card|bank.?account|routing.?number)"},
]


def scan_column_names(df: DataFrame) -> Dict[str, List[str]]:
    """Scan DataFrame column names for patterns suggesting PHI.

    Args:
        df: DataFrame to scan.

    Returns:
        Dictionary mapping PHI category labels to lists of matching
        column names.
    """
    findings: Dict[str, List[str]] = {}

    for col_name in df.columns:
        for phi_pattern in PHI_COLUMN_PATTERNS:
            if re.search(phi_pattern["pattern"], col_name):
                label = phi_pattern["label"]
                if label not in findings:
                    findings[label] = []
                if col_name not in findings[label]:
                    findings[label].append(col_name)

    return findings


def scan_column_values(
    df: DataFrame, sample_size: int = 1000
) -> Dict[str, Dict[str, int]]:
    """Scan sampled column values for PHI patterns using regex.

    Only string columns are scanned. A sample of rows is collected
    to the driver for pattern matching.

    Args:
        df: DataFrame to scan.
        sample_size: Number of rows to sample for value scanning.

    Returns:
        Dictionary mapping column names to dictionaries of
        {pattern_name: match_count}.
    """
    findings: Dict[str, Dict[str, int]] = {}

    # Only scan string columns
    string_cols = [
        field.name
        for field in df.schema.fields
        if isinstance(field.dataType, StringType)
    ]

    if not string_cols:
        return findings

    sampled = df.select(string_cols).limit(sample_size)
    rows = sampled.collect()

    for col_name in string_cols:
        col_findings: Dict[str, int] = {}
        for row in rows:
            val = row[col_name]
            if val is None:
                continue
            val_str = str(val)
            for pattern_name, pattern in PHI_VALUE_PATTERNS.items():
                if re.search(pattern, val_str):
                    col_findings[pattern_name] = col_findings.get(pattern_name, 0) + 1

        if col_findings:
            findings[col_name] = col_findings

    return findings


def scan_dataframe(
    df: DataFrame, sample_size: int = 1000
) -> Dict[str, Any]:
    """Run a comprehensive PHI scan on a DataFrame.

    Combines column name analysis and value pattern matching to produce
    a full report of potential PHI in the dataset.

    Args:
        df: DataFrame to scan.
        sample_size: Number of rows to sample for value scanning.

    Returns:
        Comprehensive scan report dictionary with:
        - has_potential_phi: boolean flag
        - column_name_findings: PHI patterns found in column names
        - value_findings: PHI patterns found in column values
        - total_columns_scanned: number of columns checked
        - columns_with_phi_names: count of columns with PHI-like names
        - columns_with_phi_values: count of columns with PHI-like values
        - risk_level: "HIGH", "MEDIUM", "LOW", or "NONE"
        - recommendation: human-readable guidance
    """
    name_findings = scan_column_names(df)
    value_findings = scan_column_values(df, sample_size)

    has_phi = bool(name_findings) or bool(value_findings)
    columns_with_phi_names = sum(len(v) for v in name_findings.values())
    columns_with_phi_values = len(value_findings)

    # Determine risk level
    if value_findings and name_findings:
        risk_level = "HIGH"
    elif value_findings:
        risk_level = "HIGH"
    elif name_findings and columns_with_phi_names >= 3:
        risk_level = "MEDIUM"
    elif name_findings:
        risk_level = "LOW"
    else:
        risk_level = "NONE"

    # Generate recommendation
    if risk_level == "HIGH":
        recommendation = (
            "HIGH RISK: PHI patterns detected in column values. "
            "Apply de-identification (hashing, masking, removal) before "
            "publishing to research or external domains."
        )
    elif risk_level == "MEDIUM":
        recommendation = (
            "MEDIUM RISK: Multiple columns have PHI-like names. "
            "Review column contents and apply de-identification as needed."
        )
    elif risk_level == "LOW":
        recommendation = (
            "LOW RISK: Some column names suggest possible PHI. "
            "Verify contents before publishing to non-PHI domains."
        )
    else:
        recommendation = (
            "No PHI indicators found. Safe for research domain publication."
        )

    report: Dict[str, Any] = {
        "has_potential_phi": has_phi,
        "risk_level": risk_level,
        "column_name_findings": name_findings,
        "value_findings": value_findings,
        "total_columns_scanned": len(df.columns),
        "columns_with_phi_names": columns_with_phi_names,
        "columns_with_phi_values": columns_with_phi_values,
        "recommendation": recommendation,
    }

    return report


def print_report(report: Dict[str, Any]) -> None:
    """Print a human-readable PHI scan report to the console.

    Args:
        report: Report dictionary from scan_dataframe().
    """
    print("\n" + "=" * 60)
    print("PHI SCAN REPORT")
    print("=" * 60)
    print(f"  PHI Detected:              {'YES' if report['has_potential_phi'] else 'NO'}")
    print(f"  Risk Level:                {report['risk_level']}")
    print(f"  Total Columns Scanned:     {report['total_columns_scanned']}")
    print(f"  Columns with PHI Names:    {report['columns_with_phi_names']}")
    print(f"  Columns with PHI Values:   {report['columns_with_phi_values']}")

    if report["column_name_findings"]:
        print("\n  Column Name Findings:")
        for label, cols in report["column_name_findings"].items():
            print(f"    [{label}]: {', '.join(cols)}")

    if report["value_findings"]:
        print("\n  Value Pattern Findings:")
        for col, patterns in report["value_findings"].items():
            for pattern_name, count in patterns.items():
                print(f"    {col}: {pattern_name} ({count} matches in sample)")

    print(f"\n  Recommendation: {report['recommendation']}")
    print("=" * 60 + "\n")
