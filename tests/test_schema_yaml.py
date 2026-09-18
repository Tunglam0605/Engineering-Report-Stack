from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from report_engine.validation import load_and_validate

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "demo-report"
SCHEMAS = ROOT / "schemas"


class SchemaAndYamlTests(unittest.TestCase):
    def test_yaml_entity_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report"
            shutil.copytree(DEMO, report)

            source_json = report / "data" / "sources" / "STD-DEMO-001.json"
            source = json.loads(source_json.read_text(encoding="utf-8"))
            source_json.unlink()
            (report / "data" / "sources" / "STD-DEMO-001.yaml").write_text(
                yaml.safe_dump(source, sort_keys=False),
                encoding="utf-8",
            )

            model, diag = load_and_validate(report, SCHEMAS)
            self.assertTrue(diag.ok, "\n".join(diag.errors))
            self.assertIn("STD-DEMO-001", model.entities)

    def test_json_schema_rejects_unknown_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report"
            shutil.copytree(DEMO, report)

            req_path = report / "data" / "requirements" / "REQ-EMC-001.json"
            requirement = json.loads(req_path.read_text(encoding="utf-8"))
            requirement["typo_field"] = "must fail"
            req_path.write_text(
                json.dumps(requirement, indent=2) + "\n",
                encoding="utf-8",
            )

            _, diag = load_and_validate(report, SCHEMAS)
            self.assertFalse(diag.ok)
            self.assertTrue(
                any("typo_field" in error for error in diag.errors),
                diag.errors,
            )

    def test_missing_reference_fails_semantic_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report"
            shutil.copytree(DEMO, report)

            test_path = report / "data" / "tests" / "TEST-EMC-001.json"
            test = json.loads(test_path.read_text(encoding="utf-8"))
            test["verifies"] = ["REQ-DOES-NOT-EXIST"]
            test_path.write_text(
                json.dumps(test, indent=2) + "\n",
                encoding="utf-8",
            )

            _, diag = load_and_validate(report, SCHEMAS)
            self.assertFalse(diag.ok)
            self.assertTrue(
                any("REQ-DOES-NOT-EXIST" in error for error in diag.errors),
                diag.errors,
            )


if __name__ == "__main__":
    unittest.main()
