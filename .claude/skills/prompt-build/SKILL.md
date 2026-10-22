---
name: prompt-build
description: Regenerate the one-page HTML prompt reader (system/prompt-library.html) and the prompt-chain canvas (system/chains.canvas) from the notes in prompts/, and maintain the live Base (system/library.base). Use when the user asks to build, rebuild, refresh, or open the prompt library page, or after ingesting or rewriting prompts.
---

# prompt-build

Builds the generated outputs in `system/` from `prompts/`. Never edits `prompts/` and never reads `raw/` or `curated/`.

## What it produces
| Output | How | When it changes |
|---|---|---|
| `system/prompt-library.html` | `build.py` | Every run. Never edit by hand. |
| `system/chains.canvas` | `build.py` | Add-only. Adds nodes and edges for new `next` links and never moves or removes existing ones, so hand-arranged layouts and extra nodes survive. |
| `system/library.base` | Written once with the `obsidian-bases` skill | Not regenerated. A Base is a live query, so it updates on its own. Edit it only when the note schema changes. |

## Run
From the vault root:
```
python3 .claude/skills/prompt-build/build.py
```
Read the output:
- `warning:` lines mean a note was skipped (no fenced block under `## prompt`), uses a category missing from `system/taxonomy.md`, has a `next` link that matches no prompt, or has a canvas problem. Report them and suggest `prompt-ingest`.
- `chains.canvas: already up to date` means nothing was written. A write line reports how many nodes and edges were added.

Then tell the user the output path. Offer `open system/prompt-library.html` to view it.

## HTML reader
**Only prompts with `visibility: public` are on the page, and it never shows version history.** A note with no `visibility`, or any other value, is treated as private: it is left out and `build.py` prints a warning. For public prompts, the `## version-history` section is dropped from the page data, so the page shows only the latest version and is much smaller. Links to non-public prompts are removed from public prompts' page data, so a hidden prompt's name cannot leak through a related list: list items in `## related` that point at one are dropped, other links to one read "a private prompt", and `related`/`next` lose them. `visibility` filters the page only. The notes stay in the Git repository, and `chains.canvas`, the Base, `prompt-find`, and `prompt-lint` still see every prompt.

Self-contained (data embedded, no network). It has search (press `/`), category/status/tag filters, per-prompt copy buttons, optional placeholder fill-ins applied on copy, dark mode, and a phone layout where filters sit behind a Filters button. To change the look or the rendering, edit `template.html`; to change parsing, edit `build.py`.

- **Private comments never reach the page.** `build.py` removes Obsidian `%%comments%%` (inline and block) before embedding the data, so they are absent from the page, its search index, and anything shared from it. Comments inside code fences are kept, because they belong to a prompt.
- **Renders:** wikilinks resolved by filename, `title`, or any `aliases` entry (case-insensitive), callouts, blockquotes, tables, nested lists, `**bold**`, `*italic*`, `==highlight==`, footnotes, rules, and code fences. Block IDs (`^id`) are hidden.
- **Does not render:** math, Mermaid, inline `#tags`, inline footnotes, and image or file embeds. An embed of another prompt shows as a link, and any other embed shows as `↪ name`.
- **Fill-in:** each variable gets an input box, and Copy substitutes the values. It behaves exactly like `--set` in the `prompt-find` skill. For an XML-style placeholder such as `<industry>`, a wrapper pair `<industry>hint</industry>` keeps its tags and takes the value inside, and bare `<industry>` references become the value. `[Bracketed]` fields are replaced as plain text. The substitution function is `fillPrompt` in `template.html`; keep it in step with `fill()` in `.claude/skills/prompt-find/find.py`.

## Base (`system/library.base`)
Created with the `obsidian-bases` skill. Load it before editing the file.
- **Scope:** `file.inFolder("prompts")` and `type == "prompt"`, so `raw/` and `curated/` never appear.
- **Views:** All prompts, By category (grouped), Needs retest (`status == "needs-retest"`), Not public (`visibility != "public"`), and Recently updated (sorted by `updated`, newest first, limit 10).
- Hyphenated property names (`models-tested`, `use-case`) work as plain names in `order`.

## Canvas (`system/chains.canvas`)
Follows the `json-canvas` skill. One `file` node per prompt that takes part in a `next` chain, and a labelled arrow for each link. IDs are stable hashes of the slug, so rebuilds never rename anything. `build.py` checks the skill's validation list (unique IDs, edges that resolve, required fields) and refuses to write a canvas that fails it.

## Verify
1. The prompt count in the output matches the number of `.md` files in `prompts/` (minus any warned).
2. **Base check** (needs Obsidian running; optional). `base:query` only returns what the Base's filter allows, so it never lists `raw/`.
   ```
   obsidian base:query path=system/library.base view="All prompts" format=json
   ```
   The row count must equal the prompt count. Notes about the CLI: `base:views` only works on the active file, so query views by name instead. A `sort` only shows its effect when the sort property is also one of the view's columns.
3. **Tests** (run from this folder):
   ```
   python3 -I tests/test_build.py
   node tests/test_renderer.js
   ```
4. With the page open, a search for a word from one prompt finds it, and Copy puts the exact prompt block on the clipboard.
