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


def reconcile_data(input_dir: Path) -> dict[str, Any]:
    """Return keyed and aggregate reconciliation results for generated local data."""
    input_dir = input_dir.resolve()
    connection = duckdb.connect(":memory:")
    try:
        _load_ledgers(connection, input_dir)
        findings: list[dict[str, str | None]] = []
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
                findings.append(
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
        return {"currency": "SYN", "aggregate_checks": aggregates, "findings": findings}
    finally:
        connection.close()


def reconcile_to_file(input_dir: Path, output_file: Path) -> Path:
    """Run reconciliation and write a portable JSON findings file."""
    result = reconcile_data(input_dir)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return output_file
