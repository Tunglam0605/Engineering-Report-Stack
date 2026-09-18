from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


class SkillPackagingTests(unittest.TestCase):
    def test_plugin_manifest_points_to_skills(self) -> None:
        manifest = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "engineering-report-stack")
        self.assertEqual(manifest["version"], "0.2.0")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue(SKILLS.is_dir())

    def test_each_skill_matches_agent_skills_frontmatter_contract(self) -> None:
        skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
        self.assertGreaterEqual(len(skill_dirs), 1)

        for directory in skill_dirs:
            path = directory / "SKILL.md"
            self.assertTrue(path.is_file(), f"missing {path}")

            text = path.read_text(encoding="utf-8")
            match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
            self.assertIsNotNone(match, f"missing YAML frontmatter in {path}")

            metadata = yaml.safe_load(match.group(1))
            self.assertIsInstance(metadata, dict, f"frontmatter must be a map: {path}")

            name = metadata.get("name")
            description = metadata.get("description")

            self.assertIsInstance(name, str, f"missing skill name in {path}")
            self.assertIsInstance(
                description, str, f"missing skill description in {path}"
            )
            self.assertEqual(name, directory.name)
            self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertLessEqual(len(name), 64)
            self.assertTrue(description.strip())
            self.assertLessEqual(len(description), 1024)

            body = text[match.end():].strip()
            self.assertTrue(body, f"skill body must not be empty: {path}")
            self.assertLess(
                len(body.splitlines()),
                500,
                f"skill should use progressive disclosure instead of >500 lines: {path}",
            )


if __name__ == "__main__":
    unittest.main()
