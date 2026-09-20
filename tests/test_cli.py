from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from typer.testing import CliRunner

from ledger_recon.cli import app


class CliWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_help_and_complete_local_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_dir = root / "data"
            findings_file = root / "findings.json"
            report_file = root / "reconciliation-report.html"

            help_result = self.runner.invoke(app, ["--help"])
            generate_result = self.runner.invoke(app, ["generate", "--seed", "42", "--output", str(data_dir)])
            reconcile_result = self.runner.invoke(app, ["reconcile", "--input", str(data_dir), "--output", str(findings_file)])
            report_result = self.runner.invoke(app, ["report", "--findings", str(findings_file), "--output", str(report_file)])

            self.assertEqual(help_result.exit_code, 0, help_result.output)
            self.assertIn("Generate, reconcile, and report", help_result.output)
            self.assertEqual(generate_result.exit_code, 0, generate_result.output)
            self.assertEqual(reconcile_result.exit_code, 0, reconcile_result.output)
            self.assertEqual(report_result.exit_code, 0, report_result.output)
            self.assertTrue(report_file.is_file())
            self.assertIn("Synthetic ledger reconciliation audit report", report_file.read_text(encoding="utf-8"))

    def test_reconcile_rejects_missing_input_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            result = self.runner.invoke(
                app,
                ["reconcile", "--input", str(root / "missing"), "--output", str(root / "findings.json")],
            )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("existing local directory", result.output)
