import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ledger_recon.synthetic import CSV_FIELDS, generate_data


class SyntheticLedgerTest(unittest.TestCase):
    def test_generation_is_seeded_and_documents_intentional_differences(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first = generate_data(root / "first", seed=42)
            second = generate_data(root / "second", seed=42)
            for ledger_name in CSV_FIELDS:
                self.assertEqual((first / f"{ledger_name}.csv").read_text(encoding="utf-8"), (second / f"{ledger_name}.csv").read_text(encoding="utf-8"))
            with (first / "sales.csv").open(newline="", encoding="utf-8") as handle:
                sales = list(csv.DictReader(handle))
            with (first / "payments.csv").open(newline="", encoding="utf-8") as handle:
                payments = list(csv.DictReader(handle))
            manifest = json.loads((first / "discrepancies.json").read_text(encoding="utf-8"))
            self.assertEqual(len(sales), 12)
            self.assertEqual(len(payments), 11)
            self.assertNotIn("TXN-012", {row["transaction_id"] for row in payments})
            self.assertEqual(len(manifest["discrepancies"]), 4)
            self.assertEqual(manifest["discrepancies"][0]["source_row_ids"], ["SALE-009", "PAY-009"])
