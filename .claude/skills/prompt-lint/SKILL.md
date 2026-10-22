---
name: prompt-lint
description: Health-check the prompt library in prompts/ for schema problems, broken or ambiguous links, duplicates, similar tags, stale needs-retest notes, and drift between the notes and system/index.md or the generated page. Use when the user asks to lint, audit, check, validate, or clean up the library, or when they ask whether anything is broken or out of date. Reports first; fixes only metadata, with approval.
---

# prompt-lint

Finds problems in `prompts/` and the files in `system/`, then helps fix them. This follows the lint step of the LLM Wiki pattern.

## Scope
- Reads `prompts/` and the files in `system/`. **Never read, list, or touch `raw/` or `curated/`.**
- Do not use the Obsidian CLI's vault-wide `orphans`, `unresolved`, `tags`, or `search` commands. They list `raw/`. `lint.py` resolves links itself, the way Obsidian does (by filename, `title`, or any `aliases` entry).
- Reporting is read-only. The only thing the script can write is `system/index.md`, and only with `--fix-index`.
- **Never change prompt text.** Prompt text changes only through `prompt-rewrite`.

## Run
From the vault root:
```
python3 -I .claude/skills/prompt-lint/lint.py                 # full report
python3 -I .claude/skills/prompt-lint/lint.py --severity warn # errors and warnings only
python3 -I .claude/skills/prompt-lint/lint.py --json          # machine-readable
python3 -I .claude/skills/prompt-lint/lint.py --fix-index     # rewrite system/index.md
```
Exit status is 1 when there are errors. `--stale-days N` sets the needs-retest limit (default 30).

## What the script checks
| Severity | Codes |
|---|---|
| error | `missing-property`, `bad-type`, `bad-category` (not in `system/taxonomy.md`), `bad-status`, `no-frontmatter`, `no-prompt-section`, `prompt-blocks` (not exactly one), `variable-missing` (listed but not in the prompt), `broken-link`, `ambiguous-name`, `canvas-invalid` |
| warn | `missing-key`, `not-kebab`, `tag-count`, `alias-missing-title`, `use-case-long`, `bad-date`, `date-order`, `bad-version`, `history-missing`, `unlisted-variable` (`{{x}}`), `self-link`, `next-cycle`, `retired-referenced`, `stale-retest`, `duplicate-text`, `near-duplicate`, `tag-collision`, `index-missing`, `index-extra`, `index-stale`, `output-missing`, `output-stale`, `canvas-missing-file` |
| info | `nonstandard-heading`, `link-mismatch`, `no-models-tested`, `isolated`, `empty-category`, `log-missing` |

## Steps
1. **Run the report.** Read it all. Summarise by severity, naming the notes. Lead with errors.
2. **Judge what the script cannot.** Read the affected notes and the index, and add checks that need meaning:
   - **Tag collisions:** check whether the similar tags really mean the same thing before merging. For example `persona` (an AI persona) and `personas` (customer personas) are different ideas.
   - **Category fit:** does each note's category match what its prompt does?
   - **Overlap by meaning:** prompts that do nearly the same job with different words (the script only catches similar wording).
   - **Contradictions inside a prompt:** instructions that conflict with each other. Report them. Do not fix them here.
   - **Chains:** prompts that obviously belong in a sequence but have no `next` link.
3. **Propose fixes** in a table: note, problem, proposed change, and whether it is a metadata fix. Wait for approval.
4. **Apply approved fixes.** Metadata only:
   - missing keys, aliases, kebab-case tags and names (rename through Obsidian so links update: `obsidian rename path="prompts/<old>.md" name="<new>"`),
   - `related`/`next` links, `models-tested`, `status` when the user says so,
   - `index-*` findings: show what will change, then run `--fix-index`.
   Text problems (duplicate prompts, contradictions) go to the user. Offer `prompt-rewrite` for wording, or tell them to delete or merge notes themselves. Do not delete notes.
5. **After any change**, run `prompt-build` if the page, Base, or canvas is reported stale, append one line to `system/log.md` (`## [<date>] lint | <what changed>`), and re-run the linter to confirm.

## Report format
Start with one line: notes checked, errors, warnings, notes. Then errors, then warnings, grouped by code, each with the note name and the fix. Keep `info` short: mention only what is useful now. `no-models-tested` and `isolated` are reminders, not problems.

## Tests
From this folder: `python3 -I tests/test_lint.py`. They plant each defect in a throwaway vault and check the right finding appears.
