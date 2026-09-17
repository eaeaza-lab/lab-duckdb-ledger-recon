"""DuckDB-backed reconciliation of the local synthetic ledger CSV files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb


CHECKS = (
    ("payment_to_sales", "payments", "payment_row_id", "paid_amount", "gross_amount"),
    ("invoice_to_sales", "invoices", "invoice_row_id", "invoice_total", "gross_amount"),
    ("tax_ledger_to_sales", "tax_ledger", "tax_row_id", "tax_amount", "tax_amount"),
)

UNCLASSIFIED_RULE = "unclassified_reconciliation_difference"


def _amount(value: Any) -> str | None:
    """Format DuckDB decimal values as auditable two-decimal strings."""
    return None if value is None else f"{value:.2f}"


def _load_ledgers(connection: duckdb.DuckDBPyConnection, input_dir: Path) -> None:
    """Create typed temporary views over the four required local CSV files."""
    required = ("sales", "payments", "invoices", "tax_ledger")
    missing = [name for name in required if not (input_dir / f"{name}.csv").is_file()]
    if missing:
        raise FileNotFoundError(f"Missing required ledger CSV file(s): {', '.join(missing)}")

    connection.execute(
        f"""CREATE VIEW sales AS
        SELECT sale_row_id, transaction_id, currency,
               CAST(gross_amount AS DECIMAL(18, 2)) AS gross_amount,
               CAST(tax_amount AS DECIMAL(18, 2)) AS tax_amount
        FROM read_csv_auto('{input_dir / "sales.csv"}')""",
    )
    for ledger_name, row_id, amount_column in (
        ("payments", "payment_row_id", "paid_amount"),
        ("invoices", "invoice_row_id", "invoice_total"),
        ("tax_ledger", "tax_row_id", "tax_amount"),
    ):
        connection.execute(
            f"""CREATE VIEW {ledger_name} AS
            SELECT {row_id}, transaction_id, currency,
                   CAST({amount_column} AS DECIMAL(18, 2)) AS amount
            FROM read_csv_auto('{input_dir / f"{ledger_name}.csv"}')""",
        )


def _source_row_ids(finding: dict[str, str | None]) -> list[str]:
    """Return source identifiers present in a raw reconciliation finding."""
    return [row_id for row_id in (finding["sale_row_id"], finding["ledger_row_id"]) if row_id is not None]


def _load_explanations(input_dir: Path) -> dict[tuple[str, str], dict[str, Any]]:
    """Index documented synthetic discrepancy rules by check and transaction."""
    manifest_file = input_dir / "discrepancies.json"
    if not manifest_file.is_file():
        raise FileNotFoundError(f"Missing required discrepancy manifest: {manifest_file}")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    discrepancies = manifest.get("discrepancies")
    if not isinstance(discrepancies, list):
        raise ValueError("The discrepancy manifest must contain a discrepancies list")
    explanations: dict[tuple[str, str], dict[str, Any]] = {}
    for discrepancy in discrepancies:
        if not isinstance(discrepancy, dict):
            raise ValueError("Each discrepancy manifest entry must be an object")
        transaction_id = discrepancy.get("transaction_id")
        check_id = discrepancy.get("check_id")
        if not isinstance(transaction_id, str) or not isinstance(check_id, str):
            raise ValueError("Each discrepancy manifest entry needs a check_id and transaction_id")
        key = (check_id, transaction_id)
        if key in explanations:
            raise ValueError("Each discrepancy manifest entry needs a unique check_id and transaction_id")
        explanations[key] = discrepancy
    return explanations


def _explain_finding(finding: dict[str, str | None], explanations: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]:
    """Attach documented provenance, or clearly mark an unexpected difference."""
    source_row_ids = _source_row_ids(finding)
    documented = explanations.get((finding["check_id"] or "", finding["transaction_id"] or ""))
    if documented is None:
        classification = "unclassified_missing_record" if finding["expected_amount"] is None or finding["observed_amount"] is None else "unclassified_amount_variance"
        return {**finding, "classification": classification, "rule_id": UNCLASSIFIED_RULE, "rule_description": "No documented synthetic discrepancy rule matches this finding.", "source_row_ids": source_row_ids}
    documented_row_ids = documented.get("source_row_ids")
    if not isinstance(documented_row_ids, list) or not all(isinstance(row_id, str) for row_id in documented_row_ids):
        raise ValueError(f"Discrepancy rule for {finding['transaction_id']} has invalid source_row_ids")
    if not set(source_row_ids).issubset(documented_row_ids):
        raise ValueError(f"Discrepancy rule for {finding['transaction_id']} does not preserve finding source rows")
    for field in ("classification", "rule_id", "rule_description"):
        if not isinstance(documented.get(field), str):
            raise ValueError(f"Discrepancy rule for {finding['transaction_id']} is missing {field}")
    return {**finding, "classification": documented["classification"], "rule_id": documented["rule_id"], "rule_description": documented["rule_description"], "source_row_ids": documented_row_ids}


def reconcile_data(input_dir: Path) -> dict[str, Any]:
    """Return keyed and aggregate reconciliation results for generated local data."""
    input_dir = input_dir.resolve()
    connection = duckdb.connect(":memory:")
    try:
        _load_ledgers(connection, input_dir)
        raw_findings: list[dict[str, str | None]] = []
        aggregates: list[dict[str, str]] = []
        for check_id, source_ledger, row_id_column, _, sales_amount_column in CHECKS:
            rows = connection.execute(
                f"""SELECT COALESCE(s.transaction_id, l.transaction_id), s.sale_row_id, l.{row_id_column},
                           s.{sales_amount_column} AS expected_amount, l.amount AS observed_amount,
                           s.{sales_amount_column} - l.amount AS difference_amount
                    FROM sales AS s
                    FULL OUTER JOIN {source_ledger} AS l USING (transaction_id)
                    WHERE s.{sales_amount_column} IS NULL OR l.amount IS NULL
                       OR s.{sales_amount_column} <> l.amount
                    ORDER BY transaction_id"""
            ).fetchall()
            for transaction_id, sale_row_id, ledger_row_id, expected, observed, difference in rows:
                raw_findings.append(
                    {
                        "check_id": check_id,
                        "transaction_id": transaction_id,
                        "sale_row_id": sale_row_id,
                        "ledger_row_id": ledger_row_id,
                        "expected_amount": _amount(expected),
                        "observed_amount": _amount(observed),
                        "difference_amount": _amount(difference),
                    }
                )
            expected_total = connection.execute(f"SELECT SUM({sales_amount_column}) FROM sales").fetchone()[0]
            observed_total = connection.execute(f"SELECT SUM(amount) FROM {source_ledger}").fetchone()[0]
            aggregates.append(
                {
                    "check_id": check_id,
                    "expected_total": _amount(expected_total),
                    "observed_total": _amount(observed_total),
                    "difference_amount": _amount(expected_total - observed_total),
                }
            )
        explanations = _load_explanations(input_dir)
        findings = [_explain_finding(finding, explanations) for finding in raw_findings]
        return {"currency": "SYN", "aggregate_checks": aggregates, "findings": findings}
    finally:
        connection.close()


def reconcile_to_file(input_dir: Path, output_file: Path) -> Path:
    """Run reconciliation and write a portable JSON findings file."""
    result = reconcile_data(input_dir)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return output_file
