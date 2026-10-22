#!/usr/bin/env python3
"""Build system/prompt-library.html from the notes in prompts/. Standard library only.

Usage: python3 build.py [--vault PATH]
"""
import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
SECTION_ORDER = ["when-to-use", "notes", "examples", "related"]
HIDDEN_SECTIONS = {"prompt", "version-history"}  # the page shows only the latest version
VISIBILITIES = {"public", "private"}
WIKILINK_ANY = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


def split_inline_list(s):
    items, buf, quote = [], "", None
    for ch in s:
        if quote:
            if ch == quote:
                quote = None
            else:
                buf += ch
        elif ch in "\"'":
            quote = ch
        elif ch == ",":
            items.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        items.append(buf.strip())
    return items


def parse_scalar(raw):
    s = raw.strip()
    if s[:1] in "\"'":
        q = s[0]
        end = s.find(q, 1)
        return s[1:end] if end > 0 else s[1:]
    s = re.split(r"\s+#", s, maxsplit=1)[0].strip()
    if s.startswith("[") and s.endswith("]"):
        return split_inline_list(s[1:-1])
    return s


def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return {}, text
    fm, lines, i = {}, m.group(1).split("\n"), 0
    while i < len(lines):
        km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
        i += 1
        if not km:
            continue
        key, val = km.group(1), km.group(2)
        if val.strip() == "" or val.strip().startswith("#"):
            items = []
            while i < len(lines) and re.match(r"^\s+-\s*", lines[i]):
                items.append(parse_scalar(re.sub(r"^\s+-\s*", "", lines[i])))
                i += 1
            fm[key] = items if items else ""
        else:
            fm[key] = parse_scalar(val)
    return fm, text[m.end():]


def strip_comments(text):
    """Remove Obsidian %%comments%% (inline and block) outside code fences.

    Comments are private in Obsidian, so they must not reach the HTML page,
    its search index, or any file the page is shared from.
    """
    out, chunk, fence = [], [], None

    def flush():
        if chunk:
            out.append(re.sub(r"%%.*?%%", "", "\n".join(chunk), flags=re.S))
            chunk.clear()

    for line in text.split("\n"):
        fm = FENCE.match(line)
        if fence is None and not fm:
            chunk.append(line)
            continue
        flush()
        out.append(line)
        if fm:
            marker, info = fm.group(1), fm.group(2).strip()
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not info:
                fence = None
    flush()
    return "\n".join(out)


def split_sections(body):
    """Return {heading: text}, ignoring '## ' lines inside code fences."""
    sections, current, buf, fence = {}, None, [], None
    for line in body.split("\n"):
        fm = FENCE.match(line)
        if fm:
            marker, info = fm.group(1), fm.group(2).strip()
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not info:
                fence = None
        hm = None if fence else re.match(r"^##\s+(.*?)\s*$", line)
        if hm:
            if current is not None:
                sections[current] = "\n".join(buf).strip("\n")
            current, buf = hm.group(1).strip().lower().replace(" ", "-"), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip("\n")
    return sections


def first_fenced_block(text):
    lines, fence, out = text.split("\n"), None, []
    for line in lines:
        fm = FENCE.match(line)
        if fence is None:
            if fm:
                fence = fm.group(1)
            continue
        if fm and fm.group(1)[0] == fence[0] and len(fm.group(1)) >= len(fence) and not fm.group(2).strip():
            return "\n".join(out)
        out.append(line)
    return None


def as_list(v):
    if isinstance(v, list):
        return [x for x in v if x]
    return [v] if v else []


def load_categories(taxonomy_path):
    cats = []
    if taxonomy_path.exists():
        for line in taxonomy_path.read_text(encoding="utf-8").split("\n"):
            m = re.match(r"^\|\s*([a-z0-9-]*[a-z][a-z0-9-]*)\s*\|", line)  # needs a letter: skips the |---| row
            if m and m.group(1) != "category":
                cats.append(m.group(1))
    return cats


NODE_W, NODE_H, GAP = 400, 300, 100
CANVAS_SIDES = {"top", "right", "bottom", "left"}


def hex_id(kind, key):
    """Stable 16-char hex id, so rebuilds never rename existing nodes or edges."""
    return hashlib.sha1(f"{kind}:{key}".encode("utf-8")).hexdigest()[:16]


def validate_canvas(canvas):
    """The json-canvas skill's validation checklist. Returns a list of problems."""
    problems, ids = [], set()
    nodes, edges = canvas.get("nodes", []), canvas.get("edges", [])
    node_ids = {n.get("id") for n in nodes}
    required = {"text": "text", "file": "file", "link": "url"}
    for item in nodes + edges:
        if item.get("id") in ids:
            problems.append(f"duplicate id {item.get('id')}")
        ids.add(item.get("id"))
    for n in nodes:
        if n.get("type") not in {"text", "file", "link", "group"}:
            problems.append(f"node {n.get('id')}: bad type {n.get('type')!r}")
        for k in ("x", "y", "width", "height"):
            if not isinstance(n.get(k), int):
                problems.append(f"node {n.get('id')}: {k} must be an integer")
        need = required.get(n.get("type"))
        if need and not n.get(need):
            problems.append(f"node {n.get('id')}: missing {need}")
    for e in edges:
        for k in ("fromNode", "toNode"):
            if e.get(k) not in node_ids:
                problems.append(f"edge {e.get('id')}: {k} does not exist")
        for k in ("fromSide", "toSide"):
            if k in e and e[k] not in CANVAS_SIDES:
                problems.append(f"edge {e.get('id')}: bad {k}")
    return problems


def build_canvas(vault, prompts, warnings):
    """Add chain nodes and edges to system/chains.canvas without moving existing ones."""
    key = {}
    for p in prompts:
        for k in [p["slug"], p["title"], *p["aliases"]]:
            key[str(k).lower()] = p["slug"]
    edges = []
    for p in prompts:
        for link in p["next"]:
            m = re.match(r"\[\[([^\]|#]+)", str(link))
            target = key.get(m.group(1).strip().lower()) if m else None
            if target and target != p["slug"]:
                edges.append((p["slug"], target))
            else:
                warnings.append(f"{p['slug']}: `next` link {link!r} does not match a prompt; ignored for the canvas")
    path = vault / "system" / "chains.canvas"
    if not edges:
        print("chains.canvas: no `next` links, nothing to draw")
        return
    canvas = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"nodes": [], "edges": []}
    canvas.setdefault("nodes", [])
    canvas.setdefault("edges", [])
    by_file = {n["file"]: n for n in canvas["nodes"] if n.get("type") == "file" and n.get("file")}

    # depth of each prompt along `next` links (longest path from a chain start)
    members = sorted({s for e in edges for s in e})
    depth = {s: 0 for s in members}
    for _ in range(len(members)):
        for a, b in edges:
            depth[b] = max(depth[b], depth[a] + 1)
    if max(depth.values()) >= len(members):
        warnings.append("`next` links contain a cycle; canvas layout may be off")

    def rect(n):
        return n["x"], n["y"], n["x"] + n["width"], n["y"] + n["height"]

    def free(x, y):
        return all(
            x + NODE_W + 20 <= r[0] or x >= r[2] + 20 or y + NODE_H + 20 <= r[1] or y >= r[3] + 20
            for r in map(rect, canvas["nodes"])
        )

    bottom = max((n["y"] + n["height"] for n in canvas["nodes"]), default=-GAP) + GAP
    added_nodes = added_edges = 0
    for slug in sorted(members, key=lambda s: (depth[s], s)):
        file = f"prompts/{slug}.md"
        if file in by_file:
            continue
        preds = [by_file[f"prompts/{a}.md"] for a, b in edges if b == slug and f"prompts/{a}.md" in by_file]
        succs = [by_file[f"prompts/{b}.md"] for a, b in edges if a == slug and f"prompts/{b}.md" in by_file]
        if preds:
            x, y = preds[0]["x"] + NODE_W + GAP, preds[0]["y"]
        elif succs:
            x, y = succs[0]["x"] - NODE_W - GAP, succs[0]["y"]
        else:
            x, y = depth[slug] * (NODE_W + GAP), bottom
        while not free(x, y):
            y += NODE_H + GAP
        node = {"id": hex_id("node", slug), "type": "file", "file": file,
                "x": x, "y": y, "width": NODE_W, "height": NODE_H}
        canvas["nodes"].append(node)
        by_file[file] = node
        added_nodes += 1
    have = {(e.get("fromNode"), e.get("toNode")) for e in canvas["edges"]}
    for a, b in edges:
        fa, fb = by_file[f"prompts/{a}.md"]["id"], by_file[f"prompts/{b}.md"]["id"]
        if (fa, fb) not in have:
            canvas["edges"].append({"id": hex_id("edge", f"{a}>{b}"), "fromNode": fa, "fromSide": "right",
                                    "toNode": fb, "toSide": "left", "toEnd": "arrow", "label": "next"})
            added_edges += 1
    stale = [f for f in by_file if not (vault / f).exists()]
    for f in stale:
        warnings.append(f"chains.canvas: node for {f} points to a missing file; left in place")
    problems = validate_canvas(canvas)
    if problems:
        warnings.append("chains.canvas not written, validation failed: " + "; ".join(problems))
        return
    if added_nodes or added_edges or not path.exists():
        path.write_text(json.dumps(canvas, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {path} (+{added_nodes} nodes, +{added_edges} edges; {len(canvas['nodes'])} nodes total)")
    else:
        print("chains.canvas: already up to date")


def scrub_hidden_links(prompt, hidden_keys):
    """Remove every reference to a non-public prompt from a public prompt's page data.

    Hidden prompts must not leak through their names, so list items in `## related` that link to
    one are dropped, other links to one become "a private prompt", and `related`/`next` lose them.
    """
    def is_hidden(link):
        return link.strip().lower() in hidden_keys

    def drop_links(text):
        return WIKILINK_ANY.sub(lambda m: "a private prompt" if is_hidden(m.group(1)) else m.group(0), text)

    sections = {}
    for name, text in prompt["sections"].items():
        if name == "related":
            text = "\n".join(line for line in text.split("\n")
                             if not any(is_hidden(m) for m in WIKILINK_ANY.findall(line)))
        text = drop_links(text)
        if text.strip():
            sections[name] = text
    prompt["sections"] = sections
    for key in ("related", "next"):
        prompt[key] = [v for v in prompt[key] if not any(is_hidden(m) for m in WIKILINK_ANY.findall(str(v)))]
    return prompt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=str(Path(__file__).resolve().parents[3]))
    args = ap.parse_args()
    vault = Path(args.vault)
    prompts_dir, system = vault / "prompts", vault / "system"
    categories = load_categories(system / "taxonomy.md")

    prompts, warnings = [], []
    for path in sorted(prompts_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        sections = split_sections(strip_comments(body))
        prompt = first_fenced_block(sections.get("prompt", ""))
        slug = path.stem
        if prompt is None:
            warnings.append(f"{slug}: no fenced block under '## prompt'; skipped")
            continue
        category = fm.get("category", "") or "uncategorised"
        if categories and category not in categories:
            warnings.append(f"{slug}: category '{category}' is not in taxonomy.md")
        ordered = {k: sections[k] for k in SECTION_ORDER if sections.get(k, "").strip()}
        for k, v in sections.items():
            if k not in ordered and k not in HIDDEN_SECTIONS and v.strip():
                ordered[k] = v
        visibility = str(fm.get("visibility", "")).strip().lower()
        if visibility not in VISIBILITIES:
            warnings.append(f"{slug}: " + (f"visibility {visibility!r} is not public or private" if visibility else "no `visibility`")
                            + "; treated as private and left off the page")
        prompts.append({
            "slug": slug,
            "title": fm.get("title") or slug.replace("-", " ").capitalize(),
            "aliases": as_list(fm.get("aliases")),
            "visibility": visibility,
            "category": category,
            "tags": as_list(fm.get("tags")),
            "status": fm.get("status", "") or "unknown",
            "models": as_list(fm.get("models-tested")),
            "source": fm.get("source", ""),
            "variables": as_list(fm.get("variables")),
            "useCase": fm.get("use-case", ""),
            "related": as_list(fm.get("related")),
            "next": as_list(fm.get("next")),
            "updated": str(fm.get("updated", "")),
            "version": str(fm.get("version", "")),
            "prompt": prompt,
            "sections": ordered,
        })

    # The page shows public prompts only. The canvas below still sees every prompt.
    public = [p for p in prompts if p["visibility"] == "public"]
    hidden = [p for p in prompts if p["visibility"] != "public"]
    public_keys = {str(k).lower() for p in public for k in [p["slug"], p["title"], *p["aliases"]]}
    hidden_keys = {str(k).lower() for p in hidden for k in [p["slug"], p["title"], *p["aliases"]]} - public_keys
    page = []
    for p in public:
        q = scrub_hidden_links(dict(p, sections=dict(p["sections"])), hidden_keys)
        q.pop("visibility")
        page.append(q)

    cat_order = [c for c in categories if any(p["category"] == c for p in page)]
    cat_order += sorted({p["category"] for p in page} - set(cat_order))
    data = {
        "generated": datetime.date.today().isoformat(),
        "categories": cat_order,
        "prompts": sorted(page, key=lambda p: p["title"].lower()),
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    template = (Path(__file__).parent / "template.html").read_text(encoding="utf-8")
    if "/*__DATA__*/null" not in template:
        sys.exit("template.html is missing the /*__DATA__*/null placeholder")
    out = system / "prompt-library.html"
    out.write_text(template.replace("/*__DATA__*/null", payload), encoding="utf-8")

    print(f"wrote {out} ({len(page)} public prompts, {len(cat_order)} categories"
          + (f"; {len(hidden)} not public and left off the page" if hidden else "") + ")")
    build_canvas(vault, prompts, warnings)
    for w in warnings:
        print("warning:", w)


if __name__ == "__main__":
    main()
