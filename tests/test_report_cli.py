from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "report_cli.py"
DEMO = ROOT / "examples" / "demo-report"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class ReportCliTests(unittest.TestCase):
    def test_demo_validates(self) -> None:
        result = run_cli("validate", str(DEMO))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("validation passed", result.stdout)

    def test_inspect_shows_canonical_tree(self) -> None:
        result = run_cli("inspect", str(DEMO))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("REPORT RPT-DEMO-001", result.stdout)
        self.assertIn("REQ-EMC-001", result.stdout)
        self.assertIn("RELATIONS 4", result.stdout)

    def test_trace_resolves_full_chain(self) -> None:
        result = run_cli("trace", str(DEMO), "REQ-EMC-001")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("STD-DEMO-001", result.stdout)
        self.assertIn("TEST-EMC-001", result.stdout)
        self.assertIn("RES-EMC-001", result.stdout)
        self.assertIn("EVD-EMC-001", result.stdout)

    def test_impact_is_downstream_only(self) -> None:
        result = run_cli("impact", str(DEMO), "STD-DEMO-001")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("requirement  1", result.stdout)
        self.assertIn("evidence     1", result.stdout)
        self.assertIn("total        4", result.stdout)

    def test_generate_creates_markdown_and_view_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.md"
            view_model = Path(tmp) / "report.json"
            result = run_cli(
                "generate",
                str(DEMO),
                str(output),
                "--view-model-output",
                str(view_model),
                "--data-url",
                "/generated/test.json",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            text = output.read_text(encoding="utf-8")
            self.assertIn("Traceability graph", text)
            self.assertIn("EntityExplorer", text)
            self.assertIn("REQ-EMC-001", text)
            self.assertIn("EVD-EMC-001", text)

            model = json.loads(view_model.read_text(encoding="utf-8"))
            self.assertEqual(model["report"]["id"], "RPT-DEMO-001")
            self.assertEqual(len(model["entities"]), 5)
            self.assertEqual(len(model["edges"]), 4)


if __name__ == "__main__":
    unittest.main()
