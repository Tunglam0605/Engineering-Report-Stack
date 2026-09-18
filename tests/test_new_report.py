from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "new_report.py"
CLI = ROOT / "tools" / "report_cli.py"


class NewReportTests(unittest.TestCase):
    def test_new_report_is_immediately_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "my-report"

            create = subprocess.run(
                [
                    "python3",
                    str(TOOL),
                    str(destination),
                    "--id",
                    "RPT-TEST-001",
                    "--name",
                    "Test Report",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

            report = json.loads((destination / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["id"], "RPT-TEST-001")

            validate = subprocess.run(
                ["python3", str(CLI), "validate", str(destination)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)
            self.assertIn("validation passed", validate.stdout)


if __name__ == "__main__":
    unittest.main()
