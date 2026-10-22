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


class Visibility(unittest.TestCase):
    """The page shows public prompts only, never version history, and never names a hidden prompt."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = Path(self.tmp.name)
        (self.vault / "prompts").mkdir()
        (self.vault / "system").mkdir()
        (self.vault / "system" / "taxonomy.md").write_text("| category | use for |\n|---|---|\n| writing | w |\n| secret-area | s |\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def note(self, slug, visibility, title=None, category="writing", extra="", nxt="[]", related="[]", prompt=None):
        vis = "" if visibility is None else f"visibility: {visibility}\n"
        title = title or slug
        (self.vault / "prompts" / f"{slug}.md").write_text(
            f"---\ntype: prompt\ntitle: {title}\naliases:\n  - Alias of {slug}\ncategory: {category}\ntags: [t]\nstatus: verified\n{vis}"
            f"use-case: use {slug}\nrelated: {related}\nnext: {nxt}\nversion: 2\n---\n## prompt\n\n```\n{prompt or 'text ' + slug}\n```\n\n{extra}",
            encoding="utf-8")

    def build(self):
        import subprocess
        out = subprocess.run([sys.executable, "-I", str(HERE / "build.py"), "--vault", str(self.vault)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        html = (self.vault / "system" / "prompt-library.html").read_text(encoding="utf-8")
        import re
        data = json.loads(re.search(r"const DATA = (.*?);\nconst state", html, re.S).group(1).replace("<\\/", "</"))
        return data, html, out.stdout

    def test_only_public_prompts_are_on_the_page(self):
        self.note("pub", "public")
        self.note("priv", "private")
        self.note("missing", None)
        self.note("odd", "Public-ish")
        data, html, out = self.build()
        self.assertEqual([p["slug"] for p in data["prompts"]], ["pub"])
        for hidden in ("priv", "missing", "odd"):
            self.assertNotIn(f"text {hidden}", html)
        self.assertIn("treated as private", out)
        self.assertIn("3 not public", out)

    def test_visibility_is_case_insensitive_and_trimmed(self):
        self.note("pub", " Public ")
        data, _, _ = self.build()
        self.assertEqual(len(data["prompts"]), 1)

    def test_version_history_never_reaches_the_page(self):
        self.note("pub", "public", extra="## notes\n\nVisible note.\n\n## version-history\n\n### v1 (old)\n\n```\nOLDTEXT\n```\n")
        data, html, _ = self.build()
        self.assertEqual(list(data["prompts"][0]["sections"]), ["notes"])
        self.assertNotIn("OLDTEXT", html)

    def test_categories_used_only_by_hidden_prompts_are_not_listed(self):
        self.note("pub", "public", category="writing")
        self.note("priv", "private", category="secret-area")
        data, html, _ = self.build()
        self.assertEqual(data["categories"], ["writing"])
        self.assertNotIn("secret-area", html)

    def test_hidden_prompts_are_not_named_by_links(self):
        self.note("priv", "private", title="Hidden Title")
        self.note("pub", "public", related='["[[priv]]", "[[pub2]]"]', nxt='["[[Alias of priv]]"]',
                  extra="## notes\n\nSee [[priv]] and [[Hidden Title|shown label]] and [[pub2]].\n\n"
                        "## related\n\n- [[priv]]: secret reason\n- [[pub2]]: ok reason\n")
        self.note("pub2", "public")
        data, html, _ = self.build()
        pub = next(p for p in data["prompts"] if p["slug"] == "pub")
        self.assertEqual(pub["related"], ["[[pub2]]"])
        self.assertEqual(pub["next"], [])
        self.assertNotIn("secret reason", pub["sections"]["related"])
        self.assertIn("ok reason", pub["sections"]["related"])
        self.assertIn("a private prompt", pub["sections"]["notes"])
        self.assertIn("[[pub2]]", pub["sections"]["notes"])
        for leaked in ("Hidden Title", "shown label", "text priv", "Alias of priv", "secret reason"):
            self.assertNotIn(leaked, html)

    def test_a_name_shared_with_a_public_prompt_is_not_scrubbed(self):
        self.note("priv", "private", title="Shared")
        self.note("pub", "public", title="Shared", extra="## notes\n\nSee [[Shared]].\n")
        data, _, _ = self.build()
        self.assertIn("[[Shared]]", data["prompts"][0]["sections"]["notes"])

    def test_the_canvas_still_includes_hidden_prompts(self):
        self.note("a", "public", nxt='["[[b]]"]')
        self.note("b", "private")
        self.build()
        canvas = json.loads((self.vault / "system" / "chains.canvas").read_text(encoding="utf-8"))
        self.assertEqual({n["file"] for n in canvas["nodes"]}, {"prompts/a.md", "prompts/b.md"})

    def test_no_public_prompts_gives_an_empty_page(self):
        self.note("priv", "private")
        data, html, out = self.build()
        self.assertEqual(data["prompts"], [])
        self.assertNotIn('"slug"', html)


if __name__ == "__main__":
    unittest.main()
