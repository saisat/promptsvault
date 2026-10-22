---
name: prompt-find
description: Find the right prompt in the user's prompt library for a task and hand it over ready to paste. Use when the user asks which prompt to use, wants a prompt for a job ("something to stress-test a plan", "a prompt for a LinkedIn post"), asks "do I have a prompt for...", or asks to search, find, look up, or list prompts in the library. Read-only; can fill in a prompt's placeholders and copy it to the clipboard.
---

# prompt-find

Matches a need to the prompts in `prompts/` and returns the best ones with a copy-ready block. It never changes the library.

## Scope
- Reads only `prompts/` (and `system/index.md`, `system/taxonomy.md`). **Never read, list, or search `raw/` or `curated/`.**
- Read-only. It writes no notes and does not edit the index or log.
- Do not use vault-wide Obsidian CLI commands such as `obsidian search`, `tags`, or `files`. They list `raw/`. Use `find.py` below, or `obsidian base:query path=system/library.base view="<name>"`, which only returns what the Base's filter allows.

## The helper
`find.py` does the reliable part: weighted matching over title, aliases, tags, category, use-case, notes, and prompt text, with filters. Run it from the vault root:

```
python3 -I .claude/skills/prompt-find/find.py <words> [--category C] [--tag T] [--status S] [--limit N] [--json]
python3 -I .claude/skills/prompt-find/find.py --list [--category C] [--status S]
python3 -I .claude/skills/prompt-find/find.py --show <slug> [--set "<placeholder>=value" ...]
```

Each result carries a **fit**: `STRONG` (covers most of the query and scores well) or `WEAK`. No output ("no match") means nothing matched at all.

## Steps
1. **Understand the need.** Restate it in a few words. Ask one question only if it is too vague to search ("a good prompt"). Otherwise just search.
2. **Read `system/index.md`** to see what exists and judge candidates by meaning, not only by words.
3. **Search.** Run `find.py` with the user's words plus a few synonyms you think a matching prompt would use ("stress-test my plan" → `critique challenge feedback idea`). Run it more than once if the first query is thin. The script already knows some synonym groups (see `SYNONYM_GROUPS` in `find.py`), but your judgement is the main recall tool.
4. **Check the top candidates.** Read the note for the best 1 to 3 results (use-case, when-to-use, notes, `variables`, `status`, `related`, `next`). Decide which really fits. A `WEAK` fit is not a match unless your own reading of the note says it is.
5. **Answer.** Give the best match first, then up to two alternatives. For each: a `[[wikilink]]`, one line on why it fits, its category and `status`. Then for the best match:
   - the **copy-ready prompt**, from `find.py --show <slug>` in a fenced block, exactly as printed,
   - the **placeholders to fill** (`variables`) and an offer to fill them in from what the user said, using `--set "<placeholder>=value"`,
   - any **follow-on prompts** from `next` or `related` ("then use [[...]]").
6. **Offer the clipboard.** If the user wants it copied, pipe the same `--show` command into `pbcopy` (macOS).

## Honesty rules
- **Say the status.** If the best match is not `verified`, say so plainly (`needs-retest`, `retired`).
- **No forced matches.** If nothing is a strong fit, say the library has no good match, name the closest one and why it falls short, and offer a choice: use the closest as is, or draft a one-off adapted prompt (labelled as new, not from the library, and not saved). Suggest the user capture a proper one in `raw/` themselves; do not write there.
- **Never invent library content.** Anything not printed by `find.py --show` is not the library's prompt text.
- **Filled prompts are not saved.** `--set` changes only what is printed. The note is untouched.

## Fill-in behaviour
`--set` replaces the literal placeholder text. For an XML-style placeholder such as `<industry>`, a wrapper pair like `<industry>hint</industry>` keeps its tags and takes the value inside, and every bare `<industry>` becomes the value. For `[bracketed]` fields it replaces the bracketed text. Placeholders that do not appear in the prompt produce a warning.

## Tests
From this folder: `python3 -I tests/test_find.py`
