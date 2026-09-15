import unittest
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ledger_recon


class PackageTest(unittest.TestCase):
    def test_version_is_exposed(self) -> None:
        self.assertEqual(ledger_recon.__version__, "0.1.0")
