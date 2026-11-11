"""Offline structural checks, not evidence of agent behavior or figure quality."""

import ast
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_core_metadata_size_and_direct_navigation(self):
        core = ROOT / "SKILL.md"
        self.assertTrue(core.is_file(), "workflow draft not authored")
        text = core.read_text()
        self.assertTrue(text.startswith("---\nname: figure-generation\n"))
        frontmatter = text.split("---", 2)[1]
        self.assertRegex(frontmatter, r"\ndescription: Use when")
        self.assertNotIn("disable-model-invocation", frontmatter)
        description = frontmatter.split("description: ", 1)[1].strip()
        self.assertLessEqual(len(description), 1024)
        self.assertLessEqual(len(text.split()), 900)
        self.assertLessEqual(len(text.splitlines()), 120)
        self.assertEqual(text.count("**Complete when:**"), 5)
        links = re.findall(r"\]\(([^)]+)\)", text)
        for target in ("references/comparisons.md", "references/layout-images.md",
                       "references/matplotlib.md", "scripts/figure_style.py"):
            self.assertIn(target, links)
        self.assertNotIn("evaluations.md", text)
        self.assertNotIn("/admin/", text)

    def test_all_local_links_resolve_and_runtime_excludes_evaluation(self):
        documents = list(ROOT.rglob("*.md"))
        self.assertGreaterEqual(len(documents), 6, "conditional references/index missing")
        for path in documents:
            text = path.read_text()
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" not in target and not target.startswith("#"):
                    with self.subTest(path=path.name, target=target):
                        self.assertTrue((path.parent / target.split("#")[0]).is_file())
            if path.name != "evaluations.md":
                self.assertNotIn("evaluations.md", text)
                self.assertNotIn("/admin/", text)

    def test_python_syntax_metadata_and_text_hygiene(self):
        scripts = list(ROOT.rglob("*.py"))
        self.assertTrue(scripts)
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".py"):
                text = path.read_text()
                self.assertTrue(text.endswith("\n"), str(path))
                for number, line in enumerate(text.splitlines(), 1):
                    self.assertEqual(line, line.rstrip(), f"{path}:{number}")
                    if path.suffix == ".py":
                        self.assertLessEqual(len(line), 100, f"{path}:{number}")
        for path in scripts:
            ast.parse(path.read_text(), filename=str(path))
        helper = (ROOT / "scripts" / "figure_style.py").read_text()
        self.assertIn('# dependencies = ["matplotlib>=3.10"]', helper)
        self.assertIn("# /// script", helper)


if __name__ == "__main__":
    unittest.main()
