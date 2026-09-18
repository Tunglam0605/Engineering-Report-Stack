from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


class SkillPackagingTests(unittest.TestCase):
    def test_plugin_manifest_points_to_skills(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "engineering-report-stack")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue(SKILLS.is_dir())

    def test_each_skill_has_valid_frontmatter(self) -> None:
        skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
        self.assertGreaterEqual(len(skill_dirs), 1)

        for directory in skill_dirs:
            path = directory / "SKILL.md"
            self.assertTrue(path.is_file(), f"missing {path}")
            text = path.read_text(encoding="utf-8")
            match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
            self.assertIsNotNone(match, f"missing YAML frontmatter in {path}")
            frontmatter = match.group(1)
            name_match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", frontmatter, flags=re.MULTILINE)
            description_match = re.search(r"^description:\s*(.+)\s*$", frontmatter, flags=re.MULTILINE)
            self.assertIsNotNone(name_match, f"missing skill name in {path}")
            self.assertIsNotNone(description_match, f"missing skill description in {path}")
            self.assertEqual(name_match.group(1), directory.name)
            self.assertLessEqual(len(directory.name), 64)


if __name__ == "__main__":
    unittest.main()
