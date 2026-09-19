import json
from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ledger_recon.reconcile import reconcile_to_file
from ledger_recon.report import render_report
from ledger_recon.synthetic import generate_data


class ReportTest(unittest.TestCase):
    def test_report_is_standalone_and_includes_totals_findings_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_dir = generate_data(root / "data", seed=42)
            findings_file = reconcile_to_file(data_dir, root / "findings.json")
            report_file = render_report(findings_file, root / "reconciliation-report.html")
            report = report_file.read_text(encoding="utf-8")

        self.assertIn("<!doctype html>", report)
        self.assertIn("Ledger totals", report)
        self.assertIn("payment_to_sales", report)
        self.assertIn("TXN-009", report)
        self.assertIn("payment_amount_variance", report)
        self.assertIn("SALE-009", report)
        self.assertIn("PAY-009", report)
        self.assertIn("Missing", report)

    def test_report_escapes_finding_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            findings_file = root / "findings.json"
            findings_file.write_text(json.dumps({"currency": "SYN", "aggregate_checks": [], "findings": [{"check_id": "check", "transaction_id": "TXN-001", "expected_amount": "1.00", "observed_amount": "1.00", "difference_amount": "0.00", "classification": "test", "rule_id": "rule", "rule_description": "<script>alert(1)</script>", "source_row_ids": ["SALE-001"]}]}), encoding="utf-8")
            report = render_report(findings_file, root / "report.html").read_text(encoding="utf-8")

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", report)
        self.assertNotIn("<script>alert(1)</script>", report)
