"""Tests for find.py. Run from the skill folder: python3 -I tests/test_find.py"""
import argparse
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("find", HERE / "find.py")
find = importlib.util.module_from_spec(spec)
spec.loader.exec_module(find)


def note(slug, title, category, tags, use, body_notes="", status="verified", prompt="Do the thing.", variables="[]"):
    return (f"---\ntype: prompt\ntitle: {title}\ncategory: {category}\ntags: [{', '.join(tags)}]\nstatus: {status}\n"
            f"variables: {variables}\nuse-case: {use}\nversion: 1\n---\n## prompt\n\n```\n{prompt}\n```\n\n"
            f"## notes\n\n{body_notes}\n")


def args(**kw):
    return argparse.Namespace(**{"category": None, "tag": None, "status": None, **kw})


class Search(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = Path(self.tmp.name)
        (self.vault / "prompts").mkdir()
        self.add("mentor", "Be my ruthless mentor", "thinking-partner", ["critique", "persona"],
                 "Get blunt critique of an idea.", prompt="You are my ruthless mentor.")
        self.add("linkedin", "LinkedIn post generator", "writing", ["linkedin", "social-media"],
                 "Write a LinkedIn post from a short interview.", status="needs-retest")
        self.add("market", "Market analysis", "market-research", ["market-analysis"],
                 "Analyse an industry and its competitors.", body_notes="Visible %%SECRETWORD%% text.")
        self.notes = find.load_notes(self.vault)

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, slug, *a, **kw):
        (self.vault / "prompts" / f"{slug}.md").write_text(note(slug, *a, **kw), encoding="utf-8")

    def slugs(self, query, **kw):
        return [r["slug"] for r in find.search(self.notes, query, args(**kw))]

    def test_synonyms_find_the_mentor(self):
        results = find.search(self.notes, "something to stress-test my plan", args())
        self.assertEqual(results[0]["slug"], "mentor")
        self.assertEqual(results[0]["fit"], "strong")

    def test_off_topic_query_has_no_match(self):
        self.assertEqual(self.slugs("poem about cats"), [])

    def test_weak_hits_are_labelled_weak(self):
        results = find.search(self.notes, "write a post about competitors and markets", args())
        self.assertTrue(results)
        self.assertTrue(all(r["fit"] in ("strong", "weak") for r in results))

    def test_filters(self):
        self.assertEqual(self.slugs("post analysis critique", category="writing"), ["linkedin"])
        self.assertEqual(self.slugs("post analysis critique", status="verified").count("linkedin"), 0)
        self.assertEqual(self.slugs("post analysis critique", tag="persona"), ["mentor"])

    def test_empty_query_lists_everything(self):
        self.assertEqual(len(find.search(self.notes, "", args())), 3)

    def test_private_comments_are_not_searchable(self):
        self.assertEqual(self.slugs("secretword"), [])


class Fill(unittest.TestCase):
    def test_inline_and_wrapper_tags(self):
        text = "Industry: <industry>\nProduct: <product>\n\nMiddle line.\n\n<industry>\n</industry>\n\n<product>\n</product>"
        out = find.fill(text, [("<industry>", "Banking"), ("<product>", "Wallet")])
        self.assertEqual(out, "Industry: Banking\nProduct: Wallet\n\nMiddle line.\n\n"
                              "<industry>Banking</industry>\n\n<product>Wallet</product>")

    def test_inline_tag_never_swallows_text_up_to_a_distant_closing_tag(self):
        text = "Start <x> middle one.\nMiddle two.\n<x>hint</x>\nEnd."
        out = find.fill(text, [("<x>", "V")])
        self.assertIn("Middle two.", out)
        self.assertEqual(out, "Start V middle one.\nMiddle two.\n<x>V</x>\nEnd.")

    def test_wrapper_hint_text_is_replaced(self):
        out = find.fill("About the <cat> market.\n<cat>Name the category (for example: X)</cat>", [("<cat>", "Pets")])
        self.assertEqual(out, "About the Pets market.\n<cat>Pets</cat>")

    def test_bracket_fields(self):
        self.assertEqual(find.fill("Company:\n[Company name]", [("[Company name]", "Acme")]), "Company:\nAcme")


class Show(unittest.TestCase):
    def test_show_prints_the_exact_block_and_rejects_unknown_slugs(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp)
            (vault / "prompts").mkdir()
            (vault / "prompts" / "a.md").write_text(note("a", "A", "writing", ["t"], "u", prompt="Line 1\nLine 2"), encoding="utf-8")
            notes = find.load_notes(vault)
            self.assertEqual(notes[0]["prompt"], "Line 1\nLine 2")
            with self.assertRaises(SystemExit):
                find.show(notes, "nope", [])


if __name__ == "__main__":
    unittest.main()
