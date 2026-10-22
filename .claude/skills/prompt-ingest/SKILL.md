---
name: prompt-ingest
description: Turn a tested prompt file from curated/ into a finished, schema-conformant note in prompts/ (frontmatter, category, tags, variables, related links, kebab-case filename), then update system/index.md and system/log.md. Use when the user has put prompts in curated/ and asks to ingest, normalise, categorise, or re-categorise them, or to re-ingest an improved version. Never edits the prompt text or the source file.
---

# prompt-ingest

Reads free-form files in `curated/` and writes one finished note per prompt into `prompts/`, plus index and log bookkeeping.

## Scope
- **Input:** `curated/`, read only. Never edit, rename, or move a source file.
- **Output:** `prompts/`. This is the only place the skill creates or changes notes.
- Never read, list, or touch `raw/`.
- **The prompt text is copied exactly** from the source into `## prompt`. Not even whitespace changes. Use `prompt-rewrite` to change text afterwards.
- Read `system/schema.md` (note shape) and `system/taxonomy.md` (allowed categories) first, every run.
- Write the note in Obsidian Flavored Markdown. Load the `obsidian-markdown` skill before writing and follow its rules for properties, wikilinks, and callouts.

## Optional: obsidian-cli
If Obsidian is running (`obsidian help` succeeds), these `obsidian-cli` commands can help. If it fails with "unable to find Obsidian", use the file-based steps; do not ask the user to open it unless a step cannot be done another way.
- `obsidian backlinks path="prompts/<note>.md"` lists notes that link to an existing note (re-ingest).
- `obsidian delete path="curated/<source>.md"` moves a source file to Obsidian's trash (recoverable). Use it only after the user confirms (last step).
- Write notes with the normal file tools by default, so the user can review a diff.

**Keep `raw/` out of sight.** Many CLI commands are vault-wide (`tags`, `properties`, `search`, `orphans`, `unresolved`, `files`) and would list `raw/` content. Never run them bare. Pass `path=` or `folder=prompts`, or filter the output before reading it, e.g. `obsidian orphans | grep '^prompts/'`. For tag consistency, scan the frontmatter of the notes in `prompts/` instead of using `obsidian tags`.

## Inputs
A source filename in `curated/`, several, or "all". With "all", process the sources one at a time and show each result before moving on.

## Steps for each source
1. **Read** the source in `curated/`. Locate the prompt block (the first fenced block, usually under a heading such as "Prompt Text"). If the prompt has no fence, wrap exactly the prompt text in one and say so. Everything else in the file (usage notes, examples, test results, the author's intro, a source URL) is material for the note's other sections.
2. **Map legacy frontmatter** onto the schema: `categories`/`category` → `category`, `purpose`/`use-case`/`Goal` → `use-case`, `models` → `models-tested`, `date`/`created` → `created`, `source` → `source`. Keep valid existing values; drop empty keys.
3. **Choose the target filename**: kebab-case, derived from the title (`market-research-analysis-with-ai.md`), written to `prompts/`. Check whether it already exists:
   - **Exists → re-ingest** (see below).
   - **Doesn't exist → new note.**
4. **Fill the schema.** For each field:
   - `title`: from the H1 or the filename, in sentence case. Set `aliases` to `[<title>]` so the note is findable by its readable name.
   - `category`: pick one from `taxonomy.md`. If none fits, **stop and propose** a new category to the user; never add one silently.
   - `tags`: 2–5 kebab-case tags. Reuse tags already seen in `prompts/`; scan the other notes' frontmatter to stay consistent.
   - `variables`: every `<placeholder>` or `{{variable}}` inside the prompt block, in order, no duplicates. XML-style wrapper tags that carry the input (e.g. `<industry>…</industry>`) are not placeholders; leave them out and explain in `## notes`.
   - `status`: keep if set, otherwise `verified` (sources in `curated/` have been tested).
   - `visibility`: `public` or `private`. Keep the source's value if it has one. Otherwise set `public`, the user's default for new prompts. Only `public` prompts appear on the web page, and the value does not hide a note from the Git repository.
   - `models-tested`, `source`: keep if set. If unknown, leave `[]` / `own`. Do not invent. Move a source URL found in the file into `source`.
   - `use-case`: one line, written from the source's existing description. If there is none, draft one and flag it for review.
   - `related` / `next`: wikilinks to other notes in `prompts/` (and other sources being ingested in this run) that are clearly similar or that follow in a chain. Only link notes that exist or will exist after this run. Skip when unsure.
   - `created` / `updated`: keep `created` from the source if present, otherwise today. `updated`: today. `version`: `1` for new notes.
5. **Build the body** to the schema headings (`## prompt`, `## when-to-use`, `## notes`, `## examples`, `## related`, `## version-history`). Move the source's other prose into the matching section instead of dropping it. Leave a heading out only if empty and optional; `## version-history` may start empty.
6. **Show the user the new note** (or the diff, for a re-ingest) and wait for approval before writing.
7. **Write** the note to `prompts/`.
8. **Index.** Rewrite `system/index.md`: one `## <category>` section per category in use, each entry `- [[note-name]]: <use-case>`, sorted alphabetically, plus a total count at the top. Rebuild it from all frontmatter in `prompts/`, not by patching.
9. **Log.** Append to `system/log.md`: `## [<today>] ingest | <note-filename>` and one line naming the source file and what was done. Use `recategorise` as the operation if only the category changed, and `re-ingest` for an update.

## Re-ingest (the target note already exists)
Show a diff between the existing `prompts/` note and what the source would produce. Then, after approval:
- **Prompt text changed:** move the old text into `## version-history` as `### v<old> (<today>, replaced by re-ingest)` in its own fenced block, set the new text, bump `version`, and set `updated`.
- **Prompt text unchanged:** only merge new material from the source (extra notes, examples, test results, models).
- **Always keep** existing notes, examples, `related`/`next` links, version history, and `visibility`. Don't overwrite anything the source doesn't mention.
- `status` becomes `verified` again, since the source was tested.

## Verify before finishing
- The prompt block in the `prompts/` note is byte-identical to the prompt in the source (or, for a re-ingest, to the new text, with the old text in version history).
- `variables` matches the placeholders in the block.
- Every `related` / `next` link points to an existing note.
- `category` is in `taxonomy.md`.
- The source file in `curated/` was not modified.

## Re-categorising on demand
When the user asks to recategorise, change only `category` and `tags` of the named notes in `prompts/` (or all), show the old → new table, wait for approval, then update the index and log.

## Final message
Report notes created or updated, any category proposals waiting on the user, and the `curated/` files that passed verification. **Offer to delete those source files** and wait for the user's answer. Delete only the ones the user confirms, via `obsidian delete` (trash), and log it as `cleanup | <source-filename>`. Suggest `prompt-build` to refresh the HTML.
