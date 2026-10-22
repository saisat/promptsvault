---
name: prompt-rewrite
description: Rewrite, optimise, or improve the text of a prompt note in prompts/ using a named style profile (asd-ste100, structured, concise). Use when the user asks to rewrite, tighten, simplify, restructure, or "make X follow ASD-STE100" for a prompt in the library. This is the only skill allowed to change prompt text.
---

# prompt-rewrite

Rewrites the `## prompt` block of one note in `prompts/`, keeps the old text in version history, and flags the note for retesting.

## Scope
- Works only on notes in `prompts/`. Never read or touch `raw/`.
- Changes only the `## prompt` block, `## version-history`, and the frontmatter fields `version`, `status`, `updated`. Everything else in the note stays as is.
- Read `system/schema.md` for the note shape. Load the `obsidian-markdown` skill before editing so properties and the version-history blocks stay valid Obsidian Markdown.

## Inputs
1. **Note**: filename or title. If ambiguous, list the matching notes in `prompts/` and ask.
2. **Profile**: one of the files in `references/` (`asd-ste100`, `structured`, `concise`). If the user names none, ask which one; do not guess.
3. **Extra instruction** (optional): e.g. "keep it under 150 words".

## Steps
1. Read the note. Extract the single fenced block under `## prompt`. If there are zero or several blocks, stop and report it.
2. Read `references/<profile>.md` and follow its rules.
3. Draft the rewrite. These must survive unchanged:
   - every `<placeholder>` and `{{variable}}` exactly as written, and the `variables` list must still match,
   - the intent, constraints, and output format, unless the profile or the user's instruction says otherwise,
   - fence style (use a longer outer fence if the prompt contains triple backticks).
4. Show the user a before/after, a short list of what changed and why, and anything you were unsure about. **Wait for approval.** Offer to adjust before applying.
5. On approval, edit the note:
   - replace the block with the new text,
   - prepend the old text under `## version-history` as `### v<old-version> (<today>, replaced by <profile> rewrite)` in its own fenced block,
   - set `version` to old + 1, `updated` to today, and `status: needs-retest`,
   - add the profile name to `tags` only if the user wants it.
6. Append to `system/log.md`: `## [<today>] rewrite | <note-filename>` with one line naming the profile.
7. Tell the user the note is now `needs-retest` and offer to run `prompt-ingest` to refresh the index.

## Don't
- Don't rewrite several notes in one go without showing each diff.
- Don't "improve" beyond the profile. If the prompt seems wrong or unsafe, say so instead of silently changing its meaning.
- Don't drop the old version. It must end up in `## version-history`.
