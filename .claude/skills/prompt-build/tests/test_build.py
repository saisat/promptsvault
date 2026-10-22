"""Tests for build.py: private-comment stripping and add-only canvas generation.

Run from the skill folder: python3 -I tests/test_build.py
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True  # keep __pycache__ out of the vault

HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build", HERE / "build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def prompt(slug, nxt="[]"):
    return (f"---\ntype: prompt\ntitle: {slug}\naliases:\n  - Alias of {slug}\ncategory: writing\n"
            f"tags: [t]\nstatus: verified\nnext: {nxt}\n---\n## prompt\n\n```\ntext {slug}\n```\n")


class Comments(unittest.TestCase):
    def test_inline_and_block_removed(self):
        out = build.strip_comments("a %%X%% b\n\n%%\nSECRET\n%%\n\nc")
        self.assertNotIn("SECRET", out)
        self.assertNotIn("X", out)
        self.assertIn("a  b", out)
        self.assertIn("c", out)

    def test_fenced_comments_kept(self):
        text = "```\nkeep %%this%%\n```\nbut %%drop%% this"
        out = build.strip_comments(text)
        self.assertIn("keep %%this%%", out)
        self.assertNotIn("drop", out)


class Canvas(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = Path(self.tmp.name)
        (self.vault / "prompts").mkdir()
        (self.vault / "system").mkdir()
        self.path = self.vault / "system" / "chains.canvas"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, slug, nxt="[]"):
        (self.vault / "prompts" / f"{slug}.md").write_text(prompt(slug, nxt), encoding="utf-8")

    def run_build(self):
        prompts, warnings = [], []
        for p in sorted((self.vault / "prompts").glob("*.md")):
            fm, _ = build.parse_frontmatter(p.read_text(encoding="utf-8"))
            prompts.append({"slug": p.stem, "title": fm["title"], "aliases": build.as_list(fm.get("aliases")),
                            "next": build.as_list(fm.get("next"))})
        build.build_canvas(self.vault, prompts, warnings)
        return warnings

    def test_no_links_writes_nothing(self):
        self.write("a")
        self.run_build()
        self.assertFalse(self.path.exists())

    def test_add_only_keeps_user_edits(self):
        self.write("a", '["[[b]]"]')
        self.write("b")
        self.run_build()
        canvas = json.loads(self.path.read_text())
        for n in canvas["nodes"]:
            if n["file"].endswith("a.md"):
                n["x"], n["y"] = 1000, 500
        canvas["nodes"].append({"id": "aaaaaaaaaaaaaaaa", "type": "text", "x": -600, "y": -600,
                                "width": 300, "height": 100, "text": "mine"})
        self.path.write_text(json.dumps(canvas))
        self.write("b", '["[[Alias of c]]", "[[missing]]"]')
        self.write("c")
        warnings = self.run_build()
        canvas = json.loads(self.path.read_text())
        by_file = {n.get("file"): n for n in canvas["nodes"]}
        self.assertEqual((by_file["prompts/a.md"]["x"], by_file["prompts/a.md"]["y"]), (1000, 500))
        self.assertTrue(any(n.get("text") == "mine" for n in canvas["nodes"]))
        self.assertIn("prompts/c.md", by_file)
        self.assertEqual(build.validate_canvas(canvas), [])
        self.assertTrue(any("missing" in w for w in warnings))

    def test_rebuild_is_noop(self):
        self.write("a", '["[[b]]"]')
        self.write("b")
        self.run_build()
        first = self.path.read_bytes()
        self.run_build()
        self.assertEqual(first, self.path.read_bytes())

    def test_validation_catches_dangling_edge(self):
        bad = {"nodes": [], "edges": [{"id": "1", "fromNode": "x", "toNode": "y"}]}
        self.assertTrue(build.validate_canvas(bad))


class Taxonomy(unittest.TestCase):
    def test_separator_row_is_not_a_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "taxonomy.md"
            path.write_text("| category | use for |\n|---|---|\n| writing | drafting |\n| web-elementor | pages |\n", encoding="utf-8")
            self.assertEqual(build.load_categories(path), ["writing", "web-elementor"])


if __name__ == "__main__":
    unittest.main()
