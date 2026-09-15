"""Deterministic, local-only synthetic ledger generation."""

from __future__ import annotations

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any


ROW_COUNT = 12
CSV_FIELDS: dict[str, list[str]] = {
    "sales": ["sale_row_id", "transaction_id", "sale_date", "gross_amount", "tax_amount", "net_amount", "currency"],
    "payments": ["payment_row_id", "transaction_id", "payment_date", "paid_amount", "currency"],
    "invoices": ["invoice_row_id", "transaction_id", "invoice_date", "invoice_total", "currency"],
    "tax_ledger": ["tax_row_id", "transaction_id", "tax_date", "tax_amount", "currency"],
}


def _money(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"


def build_ledgers(seed: int, row_count: int = ROW_COUNT) -> dict[str, list[dict[str, str]]]:
    """Build synthetic ledger rows. Amounts remain decimal strings for CSV auditability."""
    if row_count < ROW_COUNT:
        raise ValueError("row_count must be at least 12 to retain documented discrepancies")
    randomizer = random.Random(seed)
    start_date = date(2026, 1, 5)
    ledgers: dict[str, list[dict[str, str]]] = {name: [] for name in CSV_FIELDS}
    for number in range(1, row_count + 1):
        transaction_id = f"TXN-{number:03d}"
        sale_date = start_date + timedelta(days=number - 1)
        gross_cents = randomizer.randrange(2_500, 60_001)
        tax_cents = (gross_cents + 5) // 10
        net_cents = gross_cents - tax_cents
        currency = "SYN"
        ledgers["sales"].append({"sale_row_id": f"SALE-{number:03d}", "transaction_id": transaction_id, "sale_date": sale_date.isoformat(), "gross_amount": _money(gross_cents), "tax_amount": _money(tax_cents), "net_amount": _money(net_cents), "currency": currency})
        if number != 12:
            paid_cents = gross_cents - 137 if number == 9 else gross_cents
            ledgers["payments"].append({"payment_row_id": f"PAY-{number:03d}", "transaction_id": transaction_id, "payment_date": (sale_date + timedelta(days=1)).isoformat(), "paid_amount": _money(paid_cents), "currency": currency})
        invoice_cents = gross_cents + 200 if number == 6 else gross_cents
        ledgers["invoices"].append({"invoice_row_id": f"INV-{number:03d}", "transaction_id": transaction_id, "invoice_date": sale_date.isoformat(), "invoice_total": _money(invoice_cents), "currency": currency})
        ledger_tax_cents = tax_cents - 50 if number == 11 else tax_cents
        ledgers["tax_ledger"].append({"tax_row_id": f"TAX-{number:03d}", "transaction_id": transaction_id, "tax_date": sale_date.isoformat(), "tax_amount": _money(ledger_tax_cents), "currency": currency})
    return ledgers


def discrepancy_manifest(seed: int) -> dict[str, Any]:
    """Return deliberate differences that future reconciliation stages must explain."""
    return {"seed": seed, "currency": "SYN", "description": "Synthetic, intentional differences for local reconciliation exercises.", "discrepancies": [
        {"rule_id": "payment_amount_variance", "source_row_ids": ["SALE-009", "PAY-009"], "transaction_id": "TXN-009", "difference_amount": "1.37"},
        {"rule_id": "invoice_total_variance", "source_row_ids": ["SALE-006", "INV-006"], "transaction_id": "TXN-006", "difference_amount": "2.00"},
        {"rule_id": "tax_amount_variance", "source_row_ids": ["SALE-011", "TAX-011"], "transaction_id": "TXN-011", "difference_amount": "0.50"},
        {"rule_id": "missing_payment", "source_row_ids": ["SALE-012"], "transaction_id": "TXN-012", "difference_amount": None},
    ]}


def generate_data(output_dir: Path, seed: int, row_count: int = ROW_COUNT) -> Path:
    """Write all synthetic ledgers and their discrepancy manifest to *output_dir*."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for ledger_name, rows in build_ledgers(seed, row_count).items():
        with (output_dir / f"{ledger_name}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS[ledger_name])
            writer.writeheader()
            writer.writerows(rows)
    with (output_dir / "discrepancies.json").open("w", encoding="utf-8") as handle:
        json.dump(discrepancy_manifest(seed), handle, indent=2)
        handle.write("\n")
    return output_dir
