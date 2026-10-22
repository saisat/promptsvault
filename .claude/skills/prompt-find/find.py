#!/usr/bin/env python3
"""Search the prompt library in prompts/. Read-only, standard library only.

Usage:
  find.py QUERY WORDS... [--category C] [--tag T] [--status S] [--limit N] [--json]
  find.py --list [--category C] [--tag T] [--status S]
  find.py --show SLUG [--set PLACEHOLDER=VALUE ...]

It reads only prompts/. It never reads raw/ or curated/.
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # do not leave __pycache__ folders in the vault

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent / "prompt-build" / "build.py"

STOP = {
    "a", "an", "and", "any", "are", "as", "at", "be", "can", "do", "for", "from", "get", "give", "have", "how", "i",
    "in", "is", "it", "me", "my", "need", "of", "on", "one", "or", "prompt", "prompts", "some", "something", "that",
    "the", "to", "use", "want", "what", "which", "with", "would", "about", "also", "by", "if", "into", "just", "like",
    "new", "no", "not", "our", "so", "their", "these", "this", "those", "using", "when", "your",
}

# Words that mean roughly the same thing here. A query word also matches its group, at lower weight.
# Edit freely: this is a plain list.
SYNONYM_GROUPS = [
    "critique challenge stress pressure grill roast feedback review blunt harsh ruthless sycophancy devil mentor",
    "write draft compose post article copywriting",
    "plan idea strategy proposal concept",
    "research analyse analyze analysis investigate study",
    "competitor competition rival landscape",
    "workshop activity exercise training session facilitator",
    "story caselet case narrative scenario fiction dilemma",
    "customer user persona buyer segment audience",
    "roadmap gtm go-to-market launch positioning",
    "library collection catalog catalogue",
]
SYNONYM_WEIGHT = 0.6

# A result is a "strong" fit only if it covers most of the query and scores well. Anything else is "weak"
# and must not be presented as a match without saying so.
STRONG_COVERAGE, STRONG_SCORE = 0.6, 8

FIELD_WEIGHTS = {"title": 5, "tags": 4, "category": 3, "use-case": 3, "notes": 1, "prompt": 1}


def load_build():
    if not BUILD.exists():
        sys.exit(f"prompt-find needs {BUILD} (the prompt-build skill) for note parsing")
    spec = importlib.util.spec_from_file_location("prompt_build", BUILD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stem(word):
    for suffix in ("ing", "ed", "es", "s"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def tokens(text):
    return [stem(w) for w in re.findall(r"[a-z0-9]+", str(text).lower()) if w not in STOP and len(w) > 1]


def synonym_map():
    groups = [{stem(w) for w in re.findall(r"[a-z0-9]+", g.lower())} for g in SYNONYM_GROUPS]
    return groups


def load_notes(vault):
    build = load_build()
    notes = []
    for path in sorted((vault / "prompts").glob("*.md")):
        fm, body = build.parse_frontmatter(path.read_text(encoding="utf-8"))
        sections = build.split_sections(build.strip_comments(body))
        notes.append({
            "slug": path.stem,
            "title": fm.get("title") or path.stem.replace("-", " ").capitalize(),
            "aliases": build.as_list(fm.get("aliases")),
            "category": fm.get("category", "") or "uncategorised",
            "tags": build.as_list(fm.get("tags")),
            "status": fm.get("status", "") or "unknown",
            "models": build.as_list(fm.get("models-tested")),
            "variables": build.as_list(fm.get("variables")),
            "use_case": fm.get("use-case", ""),
            "related": build.as_list(fm.get("related")),
            "next": build.as_list(fm.get("next")),
            "version": str(fm.get("version", "")),
            "source": fm.get("source", ""),
            "notes": "\n".join(v for k, v in sections.items() if k not in ("prompt", "version-history", "related")),
            "prompt": build.first_fenced_block(sections.get("prompt", "")) or "",
        })
    return notes


def field_tokens(note):
    return {
        "title": set(tokens(" ".join([note["title"], note["slug"], *note["aliases"]]))),
        "tags": set(tokens(" ".join(note["tags"]))),
        "category": set(tokens(note["category"])),
        "use-case": set(tokens(note["use_case"])),
        "notes": set(tokens(note["notes"])),
        "prompt": set(tokens(note["prompt"])),
    }


def score_note(note, query_tokens, groups):
    fields = field_tokens(note)
    total, matched, covered = 0.0, [], set()
    for q in query_tokens:
        related = set().union(*[g for g in groups if q in g]) - {q}
        for name, tok in fields.items():
            weight = FIELD_WEIGHTS[name]
            if q in tok:
                total += weight
                matched.append(f"{name}:{q}")
                covered.add(q)
            else:
                hit = sorted(related & tok)
                if hit:
                    total += weight * SYNONYM_WEIGHT
                    matched.append(f"{name}:{hit[0]}~{q}")
                    covered.add(q)
    coverage = len(covered) / len(query_tokens) if query_tokens else 0.0
    return round(total, 1), round(coverage, 2), matched


def passes(note, args):
    return ((not args.category or note["category"] == args.category)
            and (not args.tag or args.tag in note["tags"])
            and (not args.status or note["status"] == args.status))


def search(notes, query, args):
    qt = list(dict.fromkeys(tokens(query)))
    groups = synonym_map()
    pool = [n for n in notes if passes(n, args)]
    if not qt:
        return [dict(n, score=0, coverage=0, matched=[], fit="") for n in sorted(pool, key=lambda n: n["title"].lower())]
    results = []
    for n in pool:
        score, coverage, matched = score_note(n, qt, groups)
        if score > 0:
            fit = "strong" if coverage >= STRONG_COVERAGE and score >= STRONG_SCORE else "weak"
            results.append(dict(n, score=score, coverage=coverage, matched=matched, fit=fit))
    results.sort(key=lambda r: (-r["score"], -r["coverage"], r["title"].lower()))
    return results


def fill(text, pairs):
    """Substitute placeholders. For an XML-style placeholder such as <industry>, a wrapper pair
    <industry>hint</industry> keeps its tags and gets the value inside, and bare <industry>
    references become the value, so no stray closing tag is left."""
    for placeholder, value in pairs:
        m = re.fullmatch(r"<([^<>\s][^<>]*)>", placeholder)
        if m:
            name = re.escape(m.group(1))
            # A wrapper holds no other tag inside, so [^<]* keeps an inline "<name>" from pairing with a
            # distant closing tag and swallowing the text in between.
            text = re.sub(rf"<{name}>[^<]*</{name}>", lambda _: f"\x01{m.group(1)}\x02{value}\x03{m.group(1)}\x04", text)
            text = text.replace(placeholder, value)
            text = text.replace(f"\x01{m.group(1)}\x02", f"<{m.group(1)}>").replace(f"\x03{m.group(1)}\x04", f"</{m.group(1)}>")
        else:
            text = text.replace(placeholder, value)
    return text


def show(notes, slug, sets):
    match = next((n for n in notes if n["slug"] == slug), None)
    if not match:
        near = [n["slug"] for n in notes if slug.lower() in n["slug"] or n["slug"] in slug.lower()][:5]
        sys.exit(f"no prompt named {slug!r} in prompts/" + (f". Did you mean: {', '.join(near)}?" if near else ""))
    pairs = []
    for s in sets:
        if "=" not in s:
            sys.exit(f"--set needs PLACEHOLDER=VALUE, got {s!r}")
        k, v = s.split("=", 1)
        if k not in match["prompt"]:
            print(f"warning: {k!r} does not appear in this prompt", file=sys.stderr)
        pairs.append((k, v))
    sys.stdout.write(fill(match["prompt"], pairs))
    if not match["prompt"].endswith("\n"):
        sys.stdout.write("\n")


def brief(r):
    return {k: r[k] for k in ("slug", "title", "category", "status", "use_case", "variables", "related", "next",
                              "version", "score", "coverage", "matched", "fit")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="*", help="words describing the need")
    ap.add_argument("--category")
    ap.add_argument("--tag")
    ap.add_argument("--status")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--list", action="store_true", help="list prompts (after filters) without a query")
    ap.add_argument("--show", metavar="SLUG", help="print the copy-ready prompt block of one prompt")
    ap.add_argument("--set", action="append", default=[], metavar="PLACEHOLDER=VALUE", help="with --show: fill a placeholder")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--vault", default=str(HERE.parents[2]))
    args = ap.parse_args()
    vault = Path(args.vault)
    if not (vault / "prompts").is_dir():
        sys.exit(f"no prompts/ folder in {vault}")
    notes = load_notes(vault)
    if args.show:
        return show(notes, args.show, args.set)
    results = search(notes, "" if args.list else " ".join(args.query), args)
    if not args.list and not args.query:
        sys.exit("give some words to search for, or use --list")
    results = results if args.list else results[: args.limit]
    if args.json:
        print(json.dumps([brief(r) for r in results], ensure_ascii=False, indent=2))
        return
    if not results:
        print("no match")
        return
    for i, r in enumerate(results, 1):
        head = f"{i}. {r['slug']}  [{r['category']}, {r['status']}, v{r['version'] or '?'}]"
        print(head + (f"  {r['fit'].upper()} fit (score {r['score']}, covers {int(r['coverage'] * 100)}% of the query)" if not args.list else ""))
        print(f"   {r['use_case']}")
        if r["matched"]:
            print(f"   matched: {', '.join(r['matched'][:6])}")
        if r["variables"]:
            print(f"   fill in: {', '.join(r['variables'])}")


if __name__ == "__main__":
    main()
