"""Tests for lint.py: a clean library has no findings, and each planted defect is caught.

Run from the skill folder: python3 -I tests/test_lint.py
"""
import datetime
import importlib.util
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("lint", HERE / "lint.py")
lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint)

TODAY = datetime.date(2026, 10, 22)
PROMPT_A = "You are a careful analyst. " + " ".join(f"examine{i} item{i} report{i}." for i in range(15))
PROMPT_B = "Write a friendly note about gardening. " + " ".join(f"water{i} plant{i} morning{i}." for i in range(15))


def fm(**kw):
    base = {"type": "prompt", "title": "T", "aliases": ["T"], "category": "writing", "tags": ["alpha", "beta"],
            "status": "verified", "visibility": "public", "models-tested": ["m"], "source": "own", "variables": [], "use-case": "Does a thing.",
            "related": [], "next": [], "created": "2026-10-01", "updated": "2026-10-10", "version": 1}
    base.update(kw)
    return {k: v for k, v in base.items() if v is not None}


def render(front, prompt="Do the thing.", blocks=1, extra="", sections=True):
    lines = ["---"]
    for k, v in front.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(json.dumps(x) for x in v)}]")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    body = "\n".join(lines) + "\n"
    if sections:
        body += "## prompt\n\n" + "".join(f"```\n{prompt}\n```\n\n" for _ in range(blocks))
    return body + extra


class LintCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = Path(self.tmp.name)
        for d in ("prompts", "system", "raw", "curated"):
            (self.vault / d).mkdir()
        (self.vault / "system" / "taxonomy.md").write_text(
            "| category | use for |\n|---|---|\n| writing | w |\n| market-research | m |\n", encoding="utf-8")
        (self.vault / "raw" / "ignored.md").write_text("[[nope]] broken and ugly", encoding="utf-8")
        (self.vault / "curated" / "ignored.md").write_text("no frontmatter at all", encoding="utf-8")
        self.notes = {}

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, slug, text):
        self.notes[slug] = text
        (self.vault / "prompts" / f"{slug}.md").write_text(text, encoding="utf-8")

    def finish(self, index=True, log=True, outputs=True):
        build = lint.load_build()
        if index:
            loaded = lint.load_notes(self.vault, build)
            (self.vault / "system" / "index.md").write_text(lint.expected_index(loaded, build), encoding="utf-8")
        if log:
            (self.vault / "system" / "log.md").write_text("".join(f"## [2026-10-01] ingest | {s}.md\n" for s in self.notes), encoding="utf-8")
        if outputs:
            time.sleep(0.01)
            (self.vault / "system" / "prompt-library.html").write_text("<html></html>", encoding="utf-8")
            (self.vault / "system" / "library.base").write_text("filters: {}\n", encoding="utf-8")

    def run_lint(self, **kw):
        rep, _, _ = lint.lint(self.vault, kw.get("today", TODAY), kw.get("stale_days", 30))
        return rep

    def codes(self, rep, severity=None):
        return {(i["code"], i["slug"]) for i in rep.items if severity in (None, i["severity"])}

    def has(self, rep, code, slug=None):
        return any(i["code"] == code and (slug is None or i["slug"] == slug) for i in rep.items)


class Clean(LintCase):
    def test_a_correct_library_has_no_errors_or_warnings(self):
        self.add("note-a", render(fm(title="A", aliases=["A"], related=["[[note-b]]"], tags=["alpha", "beta"]), PROMPT_A,
                                  extra="## related\n\n- [[note-b]]: why.\n\n## version-history\n"))
        self.add("note-b", render(fm(title="B", aliases=["B"], category="market-research", tags=["gamma", "delta"]), PROMPT_B,
                                  extra="## related\n\n## version-history\n"))
        self.finish()
        rep = self.run_lint()
        self.assertEqual([i for i in rep.items if i["severity"] != "info"], [])

    def test_raw_and_curated_are_never_inspected(self):
        self.add("note-a", render(fm(), PROMPT_A))
        self.finish()
        rep = self.run_lint()
        self.assertFalse(any("ignored" in i["slug"] or "nope" in i["message"] for i in rep.items))


class Schema(LintCase):
    def check(self, text, code, severity="error", slug="n", **finish):
        self.add(slug, text)
        self.finish(**finish)
        rep = self.run_lint()
        self.assertTrue(self.has(rep, code, slug), f"{code} not found in {sorted(self.codes(rep))}")
        self.assertTrue(any(i["code"] == code and i["severity"] == severity for i in rep.items))
        return rep

    def test_missing_property(self):
        self.check(render(fm(**{"use-case": None})), "missing-property")

    def test_bad_category(self):
        self.check(render(fm(category="not-in-taxonomy")), "bad-category")

    def test_bad_status(self):
        self.check(render(fm(status="done")), "bad-status")

    def test_bad_type(self):
        self.check(render(fm(type="note")), "bad-type")

    def test_no_frontmatter(self):
        self.check("## prompt\n\n```\nx\n```\n", "no-frontmatter")

    def test_no_prompt_section(self):
        self.check(render(fm(), sections=False, extra="## notes\n\nhi\n"), "no-prompt-section")

    def test_two_prompt_blocks(self):
        self.check(render(fm(), blocks=2), "prompt-blocks")

    def test_zero_prompt_blocks(self):
        self.check(render(fm(), extra="", blocks=0), "prompt-blocks")

    def test_listed_variable_missing_from_prompt(self):
        self.check(render(fm(variables=["<gone>"]), "No placeholder here."), "variable-missing")

    def test_unlisted_double_brace_variable(self):
        self.check(render(fm(), "Hello {{name}}"), "unlisted-variable", "warn")

    def test_not_kebab_filename_tag_and_category(self):
        rep = self.check(render(fm(tags=["Bad_Tag", "ok"])), "not-kebab", "warn", slug="Bad_Name")
        self.assertGreaterEqual(sum(1 for i in rep.items if i["code"] == "not-kebab"), 2)

    def test_alias_must_include_title(self):
        self.check(render(fm(title="Real title", aliases=["Other"])), "alias-missing-title", "warn")

    def test_dates_and_version(self):
        self.check(render(fm(created="2026-10-10", updated="2026-10-01")), "date-order", "warn")
        self.check(render(fm(created="10/10/2026")), "bad-date", "warn", slug="n2")
        self.check(render(fm(version="zero")), "bad-version", "warn", slug="n3")

    def test_version_without_history(self):
        self.check(render(fm(version=3), extra="## version-history\n\n### v1 (x)\n"), "history-missing", "warn")

    def test_too_many_tags(self):
        self.check(render(fm(tags=["a1", "b2", "c3", "d4", "e5", "f6"])), "tag-count", "warn")


class Links(LintCase):
    def test_broken_link_and_self_link(self):
        self.add("n", render(fm(related=["[[missing-note]]", "[[n]]"], title="N", aliases=["N"])))
        self.finish()
        rep = self.run_lint()
        self.assertTrue(self.has(rep, "broken-link", "n"))
        self.assertTrue(self.has(rep, "self-link", "n"))

    def test_links_resolve_by_title_and_alias(self):
        self.add("a", render(fm(title="A", aliases=["A", "The A prompt"], related=["[[b]]"]), PROMPT_A))
        self.add("b", render(fm(title="Bee", aliases=["Bee", "Buzz"], related=["[[The A prompt]]", "[[buzz]]"]), PROMPT_B))
        self.finish()
        rep = self.run_lint()
        self.assertFalse(self.has(rep, "broken-link", "a"))
        self.assertFalse(self.has(rep, "broken-link", "b"))
        self.assertTrue(self.has(rep, "self-link", "b"))  # [[buzz]] is b's own alias

    def test_ambiguous_names(self):
        self.add("a", render(fm(title="Same", aliases=["Same"]), PROMPT_A))
        self.add("b", render(fm(title="Same", aliases=["Same"]), PROMPT_B))
        self.finish()
        self.assertTrue(self.has(self.run_lint(), "ambiguous-name"))

    def test_next_cycle_and_retired_target(self):
        self.add("a", render(fm(title="A", aliases=["A"], next=["[[b]]"]), PROMPT_A))
        self.add("b", render(fm(title="B", aliases=["B"], next=["[[a]]"], status="retired"), PROMPT_B))
        self.finish()
        rep = self.run_lint()
        self.assertTrue(self.has(rep, "next-cycle"))
        self.assertTrue(self.has(rep, "retired-referenced", "a"))

    def test_links_inside_prompt_text_are_ignored(self):
        self.add("a", render(fm(), "Mention [[not-a-real-note]] inside the prompt itself."))
        self.finish()
        self.assertFalse(self.has(self.run_lint(), "broken-link"))


class Duplicates(LintCase):
    def test_exact_and_near_duplicates(self):
        self.add("a", render(fm(title="A", aliases=["A"]), PROMPT_A))
        self.add("b", render(fm(title="B", aliases=["B"]), PROMPT_A))
        self.add("c", render(fm(title="C", aliases=["C"]), PROMPT_A + " One extra closing sentence here."))
        self.finish()
        rep = self.run_lint()
        self.assertTrue(self.has(rep, "duplicate-text", "b"))
        self.assertTrue(self.has(rep, "near-duplicate"))

    def test_unrelated_prompts_are_not_flagged(self):
        self.add("a", render(fm(title="A", aliases=["A"]), PROMPT_A))
        self.add("b", render(fm(title="B", aliases=["B"], tags=["gamma", "delta"]), PROMPT_B))
        self.finish()
        rep = self.run_lint()
        self.assertFalse(self.has(rep, "duplicate-text"))
        self.assertFalse(self.has(rep, "near-duplicate"))

    def test_tag_collision(self):
        self.add("a", render(fm(title="A", aliases=["A"], tags=["persona", "x1"]), PROMPT_A))
        self.add("b", render(fm(title="B", aliases=["B"], tags=["personas", "y1"]), PROMPT_B))
        self.finish()
        self.assertTrue(self.has(self.run_lint(), "tag-collision"))


class Staleness(LintCase):
    def test_old_needs_retest_is_flagged_and_recent_is_not(self):
        self.add("old", render(fm(title="Old", aliases=["Old"], status="needs-retest", updated="2026-08-01"), PROMPT_A))
        self.add("new", render(fm(title="New", aliases=["New"], status="needs-retest", updated="2026-10-20"), PROMPT_B))
        self.finish()
        rep = self.run_lint()
        self.assertTrue(self.has(rep, "stale-retest", "old"))
        self.assertFalse(self.has(rep, "stale-retest", "new"))
        self.assertFalse(self.has(self.run_lint(stale_days=365), "stale-retest"))


class IndexAndOutputs(LintCase):
    def test_index_drift(self):
        self.add("a", render(fm(title="A", aliases=["A"]), PROMPT_A))
        self.add("b", render(fm(title="B", aliases=["B"]), PROMPT_B))
        self.finish()
        index = self.vault / "system" / "index.md"
        text = index.read_text(encoding="utf-8")
        index.write_text(text.replace("Does a thing.", "An old description.", 1).replace("- [[b]]: Does a thing.\n", "")
                         + "- [[ghost]]: gone\n", encoding="utf-8")
        rep = self.run_lint()
        self.assertTrue(self.has(rep, "index-stale", "a"))
        self.assertTrue(self.has(rep, "index-missing", "b"))
        self.assertTrue(self.has(rep, "index-extra", "ghost"))

    def test_fix_index_makes_the_check_pass(self):
        self.add("a", render(fm(title="A", aliases=["A"]), PROMPT_A))
        self.finish()
        (self.vault / "system" / "index.md").write_text("# Index\n\nTotal: 0 prompts\n", encoding="utf-8")
        self.assertTrue(self.has(self.run_lint(), "index-missing", "a"))
        build = lint.load_build()
        notes = lint.load_notes(self.vault, build)
        (self.vault / "system" / "index.md").write_text(lint.expected_index(notes, build), encoding="utf-8")
        rep = self.run_lint()
        self.assertFalse([i for i in rep.items if i["code"].startswith("index-")])

    def test_missing_and_stale_outputs(self):
        self.add("a", render(fm(), PROMPT_A))
        self.finish(outputs=False)
        rep = self.run_lint()
        self.assertTrue(self.has(rep, "output-missing", "system/prompt-library.html"))
        self.assertTrue(self.has(rep, "output-missing", "system/library.base"))
        self.finish()
        html = self.vault / "system" / "prompt-library.html"
        old = html.stat().st_mtime - 100
        import os
        os.utime(html, (old, old))
        self.assertTrue(self.has(self.run_lint(), "output-stale"))

    def test_canvas_pointing_at_a_missing_file(self):
        self.add("a", render(fm(), PROMPT_A))
        self.finish()
        canvas = {"nodes": [{"id": "1", "type": "file", "file": "prompts/gone.md", "x": 0, "y": 0, "width": 1, "height": 1}], "edges": []}
        (self.vault / "system" / "chains.canvas").write_text(json.dumps(canvas), encoding="utf-8")
        self.assertTrue(self.has(self.run_lint(), "canvas-missing-file"))

    def test_log_gap_is_info_only(self):
        self.add("a", render(fm(), PROMPT_A))
        self.finish(log=False)
        (self.vault / "system" / "log.md").write_text("# Log\n", encoding="utf-8")
        rep = self.run_lint()
        self.assertTrue(any(i["code"] == "log-missing" and i["severity"] == "info" for i in rep.items))


class Visibility(LintCase):
    def test_missing_visibility_is_a_warning(self):
        self.add("n", render(fm(visibility=None)))
        self.finish()
        rep = self.run_lint()
        self.assertTrue(any(i["code"] == "missing-visibility" and i["severity"] == "warn" for i in rep.items))

    def test_invalid_visibility_is_an_error(self):
        self.add("n", render(fm(visibility="internal")))
        self.finish()
        rep = self.run_lint()
        self.assertTrue(any(i["code"] == "bad-visibility" and i["severity"] == "error" for i in rep.items))

    def test_private_prompts_get_a_reminder_not_a_warning(self):
        self.add("n", render(fm(visibility="private")))
        self.finish()
        rep = self.run_lint()
        self.assertTrue(any(i["code"] == "private-in-repo" and i["severity"] == "info" for i in rep.items))
        self.assertFalse(any(i["code"] in ("missing-visibility", "bad-visibility") for i in rep.items))

    def test_public_and_case_variants_are_fine(self):
        self.add("a", render(fm(title="A", aliases=["A"], visibility="Public"), PROMPT_A))
        self.finish()
        rep = self.run_lint()
        self.assertFalse(any("visibility" in i["code"] for i in rep.items))


if __name__ == "__main__":
    unittest.main()
