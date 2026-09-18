from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "new_report.py"
CLI = ROOT / "tools" / "report_cli.py"


class NewReportTests(unittest.TestCase):
    def test_new_yaml_report_is_immediately_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "my-report"

            create = subprocess.run(
                [
                    sys.executable,
                    str(TOOL),
                    str(destination),
                    "--id",
                    "RPT-TEST-001",
                    "--name",
                    "Test Report",
                    "--template",
                    "compliance",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

            report = yaml.safe_load(
                (destination / "report.yaml").read_text(encoding="utf-8")
            )
            self.assertEqual(report["id"], "RPT-TEST-001")
            self.assertEqual(report["metadata"]["template"], "compliance")
            self.assertTrue((destination / "REPORT_PLAN.md").is_file())

            validate = subprocess.run(
                [sys.executable, str(CLI), "validate", str(destination)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)
            self.assertIn("validation passed", validate.stdout)

    def test_json_format_remains_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "json-report"
            create = subprocess.run(
                [
                    sys.executable,
                    str(TOOL),
                    str(destination),
                    "--id",
                    "RPT-JSON-001",
                    "--name",
                    "JSON Report",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(create.returncode, 0, create.stdout + create.stderr)
            report = json.loads(
                (destination / "report.json").read_text(encoding="utf-8")
            )
            self.assertEqual(report["id"], "RPT-JSON-001")


if __name__ == "__main__":
    unittest.main()
