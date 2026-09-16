import json
from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ledger_recon.reconcile import reconcile_to_file
from ledger_recon.synthetic import generate_data


class ReconciliationTest(unittest.TestCase):
    def test_reconciliation_reports_keyed_and_aggregate_differences(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_dir = generate_data(root / "data", seed=42)
            output_file = reconcile_to_file(data_dir, root / "findings.json")
            result = json.loads(output_file.read_text(encoding="utf-8"))

        self.assertEqual(result["currency"], "SYN")
        self.assertEqual(
            [(finding["check_id"], finding["transaction_id"]) for finding in result["findings"]],
            [
                ("payment_to_sales", "TXN-009"),
                ("payment_to_sales", "TXN-012"),
                ("invoice_to_sales", "TXN-006"),
                ("tax_ledger_to_sales", "TXN-011"),
            ],
        )
        self.assertEqual(result["findings"][1]["observed_amount"], None)
        self.assertEqual(result["findings"][0]["difference_amount"], "1.37")
        self.assertEqual(
            [(check["check_id"], check["difference_amount"]) for check in result["aggregate_checks"]][1:],
            [("invoice_to_sales", "-2.00"), ("tax_ledger_to_sales", "0.50")],
        )
