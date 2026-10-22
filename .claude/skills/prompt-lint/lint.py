#!/usr/bin/env python3
"""Health check for the prompt library in prompts/. Standard library only.

Usage:
  lint.py [--severity error|warn|info] [--json] [--stale-days N]
  lint.py --fix-index        rewrite system/index.md from the notes' frontmatter

Reads prompts/ and the files in system/. It never reads raw/ or curated/.
Exit status: 1 if any error was found, otherwise 0.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True  # do not leave __pycache__ folders in the vault

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent / "prompt-build" / "build.py"

REQUIRED = ["type", "title", "category", "status", "use-case", "version", "created", "updated"]
EXPECTED_KEYS = ["aliases", "tags", "models-tested", "source", "variables", "related", "next"]
STATUSES = {"verified", "needs-retest", "retired"}
VISIBILITIES = {"public", "private"}
HEADINGS = {"prompt", "when-to-use", "notes", "examples", "related", "version-history"}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
SEVERITY_ORDER = {"error": 0, "warn": 1, "info": 2}
NEAR_DUPLICATE = 0.8


def load_build():
    if not BUILD.exists():
        sys.exit(f"prompt-lint needs {BUILD} (the prompt-build skill) for note parsing")
    spec = importlib.util.spec_from_file_location("prompt_build", BUILD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def outside_fences(text, build):
    """Text with fenced code blocks removed."""
    out, fence = [], None
    for line in text.split("\n"):
        m = build.FENCE.match(line)
        if m:
            marker, info = m.group(1), m.group(2).strip()
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not info:
                fence = None
            continue
        if fence is None:
            out.append(line)
    return "\n".join(out)


def fenced_blocks(text, build):
    blocks, fence, cur = [], None, []
    for line in text.split("\n"):
        m = build.FENCE.match(line)
        if fence is None:
            if m:
                fence, cur = m.group(1), []
            continue
        if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not m.group(2).strip():
            blocks.append("\n".join(cur))
            fence = None
        else:
            cur.append(line)
    return blocks


def stem(word):
    for suffix in ("ing", "ed", "es", "s"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def load_notes(vault, build):
    notes = []
    for path in sorted((vault / "prompts").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, body = build.parse_frontmatter(text)
        body = build.strip_comments(body)
        sections = build.split_sections(body)
        headings = [h.strip().lower().replace(" ", "-")
                    for h in re.findall(r"^##\s+(.*?)\s*$", outside_fences(body, build), re.M)]
        link_text = outside_fences(body, build)
        notes.append({
            "slug": path.stem, "path": path, "fm": fm, "has_frontmatter": text.startswith("---"),
            "sections": sections, "headings": headings,
            "blocks": fenced_blocks(sections.get("prompt", ""), build) if "prompt" in sections else [],
            "history": re.findall(r"^###\s+v(\d+)", sections.get("version-history", ""), re.M),
            "body_links": [m.strip() for m in WIKILINK.findall(link_text)],
            "related_section_links": [m.strip() for m in WIKILINK.findall(outside_fences(sections.get("related", ""), build))],
            "fm_links": [m.strip() for k in ("related", "next") for v in build.as_list(fm.get(k)) for m in WIKILINK.findall(str(v))],
            "mtime": path.stat().st_mtime,
        })
    return notes


def kebab_tags(note, build):
    return [str(t) for t in build.as_list(note["fm"].get("tags"))]


def expected_index(notes, build):
    rows = sorted(((n["fm"].get("category", "") or "uncategorised", n["slug"], str(n["fm"].get("use-case", ""))) for n in notes),
                  key=lambda r: r[1])
    out = ("# Index\n\nCatalog of every prompt in `prompts/`, grouped by category. Maintained by `prompt-ingest`.\n\n"
           f"Total: {len(rows)} prompts\n")
    for cat in sorted({r[0] for r in rows}):
        out += f"\n## {cat}\n\n" + "".join(f"- [[{s}]]: {u}\n" for c, s, u in rows if c == cat)
    return out


def parse_index(text):
    entries, cat, total = {}, None, None
    for line in text.split("\n"):
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cat = m.group(1)
        t = re.match(r"^Total:\s*(\d+)", line)
        if t:
            total = int(t.group(1))
        e = re.match(r"^-\s*\[\[([^\]|#]+)\]\]:?\s*(.*)$", line)
        if e:
            entries[e.group(1).strip()] = (cat, e.group(2).strip())
    return entries, total


class Report:
    def __init__(self):
        self.items = []

    def add(self, severity, code, slug, message, fix=""):
        self.items.append({"severity": severity, "code": code, "slug": slug, "message": message, "fix": fix})


def lint(vault, today, stale_days):
    build = load_build()
    notes = load_notes(vault, build)
    system = vault / "system"
    rep = Report()
    categories = build.load_categories(system / "taxonomy.md")

    # name resolution: filename, title, and aliases all resolve like Obsidian wikilinks
    names = defaultdict(set)
    for n in notes:
        for key in [n["slug"], str(n["fm"].get("title", "")), *build.as_list(n["fm"].get("aliases"))]:
            if key:
                names[str(key).strip().lower()].add(n["slug"])
    for key, slugs in sorted(names.items()):
        if len(slugs) > 1:
            rep.add("error", "ambiguous-name", ", ".join(sorted(slugs)),
                    f"the name {key!r} (title, alias, or filename) belongs to more than one note, so links to it are ambiguous",
                    "give each note a unique title and aliases")
    resolve = lambda t: next(iter(names[t.strip().lower()])) if len(names.get(t.strip().lower(), ())) == 1 else None

    inbound = defaultdict(set)
    texts = {}
    for n in notes:
        s, fm = n["slug"], n["fm"]
        if not n["has_frontmatter"]:
            rep.add("error", "no-frontmatter", s, "the note has no frontmatter", "run prompt-ingest on it")
            continue
        for k in REQUIRED:
            if k not in fm or fm.get(k) in ("", None):
                rep.add("error", "missing-property", s, f"required property `{k}` is missing or empty", "add it (prompt-ingest fills it in)")
        for k in EXPECTED_KEYS:
            if k not in fm:
                rep.add("warn", "missing-key", s, f"property `{k}` is absent (an empty value is fine)", f"add `{k}: []`")
        if fm.get("type") not in (None, "", "prompt"):
            rep.add("error", "bad-type", s, f"`type` is {fm.get('type')!r}, expected 'prompt'")
        cat = fm.get("category", "")
        if cat and categories and cat not in categories:
            rep.add("error", "bad-category", s, f"category {cat!r} is not in system/taxonomy.md", "pick a listed category or propose a new one to the user")
        if cat and not KEBAB.match(str(cat)):
            rep.add("warn", "not-kebab", s, f"category {cat!r} is not kebab-case")
        status = fm.get("status", "")
        if status and status not in STATUSES:
            rep.add("error", "bad-status", s, f"status {status!r} is not one of {', '.join(sorted(STATUSES))}")
        visibility = str(fm.get("visibility", "")).strip().lower()
        if not visibility:
            rep.add("warn", "missing-visibility", s, "no `visibility`, so the web page leaves this prompt out (treated as private)",
                    "add `visibility: public` or `visibility: private`")
        elif visibility not in VISIBILITIES:
            rep.add("error", "bad-visibility", s, f"visibility {fm.get('visibility')!r} is not one of {', '.join(sorted(VISIBILITIES))}")
        if not KEBAB.match(s):
            rep.add("warn", "not-kebab", s, "the filename is not kebab-case", "rename the note (Obsidian updates links)")
        tags = kebab_tags(n, build)
        for t in tags:
            if not KEBAB.match(t):
                rep.add("warn", "not-kebab", s, f"tag {t!r} is not kebab-case")
        if len(tags) > 5:
            rep.add("warn", "tag-count", s, f"{len(tags)} tags (the guideline is 2 to 5)")
        elif len(tags) < 2:
            rep.add("info", "tag-count", s, f"{len(tags)} tag(s) (the guideline is 2 to 5)")
        title = str(fm.get("title", ""))
        if title and title.lower() not in [str(a).lower() for a in build.as_list(fm.get("aliases"))]:
            rep.add("warn", "alias-missing-title", s, "`aliases` does not include the title", "add the title to aliases")
        use = str(fm.get("use-case", ""))
        if len(use) > 220:
            rep.add("warn", "use-case-long", s, f"`use-case` is {len(use)} characters; keep it to one line")
        for k in ("created", "updated"):
            if fm.get(k) and not DATE.match(str(fm[k])):
                rep.add("warn", "bad-date", s, f"`{k}` is {fm[k]!r}, expected YYYY-MM-DD")
        if DATE.match(str(fm.get("created", ""))) and DATE.match(str(fm.get("updated", ""))) and str(fm["updated"]) < str(fm["created"]):
            rep.add("warn", "date-order", s, "`updated` is earlier than `created`")
        version = str(fm.get("version", ""))
        if version and not (version.isdigit() and int(version) >= 1):
            rep.add("warn", "bad-version", s, f"`version` is {version!r}, expected a whole number of 1 or more")
        elif version.isdigit() and int(version) > 1 and len(n["history"]) < int(version) - 1:
            rep.add("warn", "history-missing", s, f"version {version} but only {len(n['history'])} entries in ## version-history",
                    "old prompt text should be kept as ### v<n> blocks")

        # body
        if "prompt" not in n["sections"]:
            rep.add("error", "no-prompt-section", s, "there is no `## prompt` section")
        else:
            if len(n["blocks"]) != 1:
                rep.add("error", "prompt-blocks", s, f"`## prompt` has {len(n['blocks'])} fenced blocks, expected exactly 1")
        for h in dict.fromkeys(n["headings"]):
            if h not in HEADINGS:
                rep.add("info", "nonstandard-heading", s, f"heading `## {h}` is not in the schema")
        block = n["blocks"][0] if n["blocks"] else ""
        texts[s] = block
        listed = [str(v) for v in build.as_list(fm.get("variables"))]
        for v in listed:
            if v not in block:
                rep.add("error", "variable-missing", s, f"variable {v!r} is listed but does not appear in the prompt", "remove it from `variables` or restore it in the prompt")
        for m in sorted(set(re.findall(r"\{\{[^{}\n]+\}\}", block))):
            if m not in listed:
                rep.add("warn", "unlisted-variable", s, f"{m} appears in the prompt but is not in `variables`")

        # links
        for link in dict.fromkeys(n["fm_links"] + n["body_links"]):
            target = resolve(link)
            if target is None:
                rep.add("error", "broken-link", s, f"[[{link}]] does not match any note in prompts/",
                        "fix the name or remove the link" if link.lower() not in names else "the name is ambiguous")
            elif target == s:
                rep.add("warn", "self-link", s, f"[[{link}]] links to the note itself")
            else:
                inbound[target].add(s)
        if set(map(str.lower, n["related_section_links"])) != set(map(str.lower, [x for x in n["fm_links"]])):
            if n["related_section_links"] or n["fm_links"]:
                rep.add("info", "link-mismatch", s, "the links in `## related` differ from `related`/`next` in the frontmatter")

    # relationships between notes
    by_slug = {n["slug"]: n for n in notes}
    for n in notes:
        for link in build.as_list(n["fm"].get("next")):
            m = WIKILINK.search(str(link))
            t = resolve(m.group(1)) if m else None
            if t and by_slug[t]["fm"].get("status") == "retired":
                rep.add("warn", "retired-referenced", n["slug"], f"`next` points at the retired prompt {t}")
    nxt = {n["slug"]: [resolve(m.group(1)) for l in build.as_list(n["fm"].get("next")) if (m := WIKILINK.search(str(l)))] for n in notes}
    for start in nxt:
        seen, stack = set(), [start]
        while stack:
            cur = stack.pop()
            for t in nxt.get(cur, []):
                if t == start:
                    rep.add("warn", "next-cycle", start, "`next` links lead back to this note")
                    stack = []
                    break
                if t and t not in seen:
                    seen.add(t)
                    stack.append(t)

    # stale status
    for n in notes:
        if n["fm"].get("status") == "needs-retest" and DATE.match(str(n["fm"].get("updated", ""))):
            age = (today - datetime.date.fromisoformat(str(n["fm"]["updated"]))).days
            if age > stale_days:
                rep.add("warn", "stale-retest", n["slug"], f"needs-retest for {age} days (limit {stale_days})", "retest it, then set status to verified")

    # duplicates
    seen_hash, token_sets = {}, {}
    for s, text in texts.items():
        if not text.strip():
            continue
        h = hashlib.sha1(re.sub(r"\s+", " ", text.lower()).strip().encode()).hexdigest()
        if h in seen_hash:
            rep.add("warn", "duplicate-text", s, f"the prompt text is identical to {seen_hash[h]}", "keep one and link or delete the other")
        seen_hash.setdefault(h, s)
        token_sets[s] = {stem(w) for w in re.findall(r"[a-z0-9]+", text.lower())}
    slugs = sorted(token_sets)
    for i, a in enumerate(slugs):
        for b in slugs[i + 1:]:
            A, B = token_sets[a], token_sets[b]
            if len(A) > 30 and len(B) > 30:
                j = len(A & B) / len(A | B)
                if j >= NEAR_DUPLICATE and hashlib.sha1(texts[a].encode()).digest() != hashlib.sha1(texts[b].encode()).digest():
                    rep.add("warn", "near-duplicate", a, f"the prompt text is {int(j * 100)}% similar to {b}", "check whether they should be one prompt")

    # tag consistency across the library
    stems = defaultdict(set)
    for n in notes:
        for t in kebab_tags(n, build):
            stems[stem(t.replace("-", ""))].add(t)
    for variants in stems.values():
        if len(variants) > 1:
            rep.add("warn", "tag-collision", "*", f"similar tags are both in use: {', '.join(sorted(variants))}", "pick one spelling and use it everywhere")

    # aggregated notes
    no_models = [n["slug"] for n in notes if n["fm"].get("status") == "verified" and not build.as_list(n["fm"].get("models-tested"))]
    if no_models:
        rep.add("info", "no-models-tested", "*", f"{len(no_models)} verified prompt(s) record no `models-tested`: {', '.join(no_models)}")
    private = [n["slug"] for n in notes if str(n["fm"].get("visibility", "")).strip().lower() == "private"]
    if private:
        rep.add("info", "private-in-repo", "*", f"{len(private)} private prompt(s) are left off the web page, but they are still readable in the Git "
                f"repository if it is public: {', '.join(private)}")
    isolated = [n["slug"] for n in notes if not inbound[n["slug"]] and not n["fm_links"] and not n["body_links"]]
    if isolated:
        rep.add("info", "isolated", "*", f"{len(isolated)} prompt(s) have no links in or out: {', '.join(isolated)}")
    used = {n["fm"].get("category") for n in notes}
    empty = [c for c in categories if c not in used]
    if empty:
        rep.add("info", "empty-category", "*", f"taxonomy categories with no prompts: {', '.join(empty)}")

    # index and log
    index_path = system / "index.md"
    if not index_path.exists():
        rep.add("warn", "index-missing", "system/index.md", "the index file does not exist", "run lint.py --fix-index")
    else:
        entries, total = parse_index(index_path.read_text(encoding="utf-8"))
        slugset = {n["slug"] for n in notes}
        for s in sorted(slugset - set(entries)):
            rep.add("warn", "index-missing", s, "the prompt is not listed in system/index.md", "run lint.py --fix-index")
        for s in sorted(set(entries) - slugset):
            rep.add("warn", "index-extra", s, "system/index.md lists a prompt that is not in prompts/", "run lint.py --fix-index")
        for n in notes:
            e = entries.get(n["slug"])
            if e and (e[0] != (n["fm"].get("category") or "uncategorised") or e[1] != str(n["fm"].get("use-case", ""))):
                rep.add("warn", "index-stale", n["slug"], "the index entry's category or use-case no longer matches the note", "run lint.py --fix-index")
        if total is not None and total != len(notes):
            rep.add("warn", "index-stale", "system/index.md", f"the index says {total} prompts but there are {len(notes)}", "run lint.py --fix-index")
    log_path = system / "log.md"
    if log_path.exists():
        logged = set(re.findall(r"\|\s*([\w.-]+)\.md", log_path.read_text(encoding="utf-8")))
        for n in notes:
            if n["slug"] not in logged:
                rep.add("info", "log-missing", n["slug"], "no entry for this prompt in system/log.md")

    # generated outputs
    html = system / "prompt-library.html"
    newest = max((n["mtime"] for n in notes), default=0)
    if not html.exists():
        rep.add("warn", "output-missing", "system/prompt-library.html", "the page has not been built", "run prompt-build")
    elif html.stat().st_mtime + 1 < newest:
        rep.add("warn", "output-stale", "system/prompt-library.html", "a note changed after the page was built", "run prompt-build")
    if not (system / "library.base").exists():
        rep.add("warn", "output-missing", "system/library.base", "the Base file does not exist", "ask for it to be created (obsidian-bases skill)")
    canvas = system / "chains.canvas"
    if canvas.exists():
        try:
            for node in json.loads(canvas.read_text(encoding="utf-8")).get("nodes", []):
                if node.get("type") == "file" and not (vault / node.get("file", "")).exists():
                    rep.add("warn", "canvas-missing-file", "system/chains.canvas", f"a node points at the missing file {node.get('file')}")
        except json.JSONDecodeError:
            rep.add("error", "canvas-invalid", "system/chains.canvas", "the canvas is not valid JSON")
    return rep, notes, build


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--severity", choices=["error", "warn", "info"], default="info", help="show this severity and worse")
    ap.add_argument("--stale-days", type=int, default=30)
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for tests")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fix-index", action="store_true")
    ap.add_argument("--vault", default=str(HERE.parents[2]))
    args = ap.parse_args()
    vault = Path(args.vault)
    if not (vault / "prompts").is_dir():
        sys.exit(f"no prompts/ folder in {vault}")
    today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
    rep, notes, build = lint(vault, today, args.stale_days)

    if args.fix_index:
        path = vault / "system" / "index.md"
        new = expected_index(notes, build)
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        if new == old:
            print("system/index.md is already up to date")
        else:
            path.write_text(new, encoding="utf-8")
            print(f"rewrote {path} ({len(notes)} prompts)")
        return

    items = sorted((i for i in rep.items if SEVERITY_ORDER[i["severity"]] <= SEVERITY_ORDER[args.severity]),
                   key=lambda i: (SEVERITY_ORDER[i["severity"]], i["code"], i["slug"]))
    counts = {s: sum(1 for i in rep.items if i["severity"] == s) for s in SEVERITY_ORDER}
    if args.json:
        print(json.dumps({"checked": len(notes), "counts": counts, "findings": items}, ensure_ascii=False, indent=2))
    else:
        print(f"prompt-lint: {len(notes)} prompts checked. {counts['error']} errors, {counts['warn']} warnings, {counts['info']} notes.")
        for sev in SEVERITY_ORDER:
            group = [i for i in items if i["severity"] == sev]
            if group:
                print(f"\n{sev.upper()}")
                for i in group:
                    print(f"  [{i['code']}] {i['slug']}: {i['message']}" + (f"  -> {i['fix']}" if i["fix"] else ""))
    sys.exit(1 if counts["error"] else 0)


if __name__ == "__main__":
    main()
