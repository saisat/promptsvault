# Log

Append-only. One entry per operation, newest last, in the form `## [YYYY-MM-DD] <operation> | <note>`.

## [2026-10-18] setup | vault scaffold
Created `curated/`, `system/`, and the `prompt-rewrite`, `prompt-ingest`, `prompt-build` skills.

## [2026-10-18] ingest | market-research-analysis-with-ai.md
Renamed from `Market Research Analysis with AI.md`. Added schema frontmatter, wrapped the prompt in a fenced block (text unchanged), moved the post intro to notes, set `source` to the LinkedIn post.

## [2026-10-18] ingest | market-research-assistant-business-model-canvas.md
Renamed from `Market Research Assistant - Business Model Canvas BMC.md`. Added schema frontmatter and restructured sections. Prompt unchanged.

## [2026-10-18] ingest | market-research-assistant-product-overview.md
Renamed from `Market Research Assistant - Product Overview.md`. Added schema frontmatter and restructured sections. Prompt unchanged.

## [2026-10-18] fix | folder model
The three ingests above wrongly edited notes inside `curated/` (the user's input folder). Corrected model: `curated/` is input, `prompts/` is the ingest output. The edited notes were discarded, the originals restored to `curated/`, and the notes will be re-ingested into `prompts/`.

## [2026-10-18] ingest | market-research-analysis-with-ai.md
Source `curated/Market Research Analysis with AI.md`. Created in `prompts/` with schema frontmatter; prompt wrapped in a fenced block (text unchanged), post intro moved to notes, `source` set to the LinkedIn post.

## [2026-10-18] ingest | market-research-assistant-business-model-canvas.md
Source `curated/Market Research Assistant - Business Model Canvas BMC.md`. Created in `prompts/` with schema frontmatter and restructured sections. Prompt unchanged.

## [2026-10-18] ingest | market-research-assistant-product-overview.md
Source `curated/Market Research Assistant - Product Overview.md`. Created in `prompts/` with schema frontmatter and restructured sections. Prompt unchanged.

## [2026-10-18] rewrite | market-research-analysis-with-ai.md
Rewrote with the asd-ste100 and structured profiles. Merged the duplicated input block and replaced the "private databases" access claim with cite-sources and no-invention rules. v1 kept in version-history; status set to needs-retest.

## [2026-10-18] rewrite | market-research-assistant-business-model-canvas.md
Rewrote with the asd-ste100 and structured profiles. Merged the duplicated element lists and turned the filled-in example (GlobeOne App) into input hint text. v1 kept in version-history; status set to needs-retest.

## [2026-10-18] rewrite | market-research-assistant-product-overview.md
Rewrote with the asd-ste100 and structured profiles. Merged the task and format lists, turned the filled-in example (Epsilon) into input hint text, and fixed the typo "string player". v1 kept in version-history; status set to needs-retest.

## [2026-10-18] ingest | linkedin-post-generator-lattice-framework.md
Source `curated/LinkedIn Post Generator - LATTICE Framework.md`. Created in `prompts/` with schema frontmatter and two notes callouts. Prompt block copied exactly (15,966 bytes). `variables` left empty because the `{field}` names are filled by the model from the user's answers.

## [2026-10-18] fix | prompt-build template
Found in browser testing of the LinkedIn prompt: callouts and blockquotes rendered as raw `> [!info]` text, and on a phone the filter list pushed results off the first screen. The template now renders callouts and blockquotes and hides filters on narrow screens behind a Filters button.

## [2026-10-18] rewrite | linkedin-post-generator-lattice-framework.md
Rewrote with the asd-ste100 and concise profiles. Instructions rewritten as short imperative sentences; questionnaire, blacklist, boundaries, `{field}` names, and numeric specs kept verbatim. Removed the duplicate blacklist entry and the stray `--` line; kept the WHY lines and FINAL REMINDER. Post-only vs metadata contradiction left as is. v1 kept in version-history; status set to needs-retest.

## [2026-10-18] ingest | ai-powered-discovery-analysis-synthesis-system-prompt.md
Source `curated/AI-Powered Discovery Analysis & Syntheis.md` (first block, "System Prompt (ChatGPT)"). The source holds two prompts, so it became two linked notes. Prompt block copied exactly.

## [2026-10-18] ingest | ai-powered-discovery-analysis-synthesis-user-prompt.md
Source `curated/AI-Powered Discovery Analysis & Syntheis.md` (second block, "User Prompt"). The nine `[bracketed]` fields are listed as `variables`. Prompt block copied exactly.

## [2026-10-18] ingest | be-my-ruthless-mentor.md
Source `curated/Be my Ruthless Mentor Prompt.md`. Mapped legacy frontmatter (`purpose` → `use-case`); dropped the empty Usage Notes and its stray `` fence. Prompt block copied exactly.

## [2026-10-18] ingest | create-fictionalized-caselet.md
Source `curated/Create Fictionalized Caselet.md`. The source description moved to `## when-to-use`; `<industry>`, `<product>`, `<product-dilemma>` listed as `variables`. Prompt block copied exactly.

## [2026-10-18] ingest | generate-ai-prompt-library-for-pms.md
Source `curated/Generate AI Prompt Library for PMs.md`. The source description moved to `## when-to-use`; `created` kept from the source date (2024-11-14). Prompt block copied exactly.

## [2026-10-18] rewrite | be-my-ruthless-mentor.md
Rewrote with the asd-ste100 and structured profiles. Kept the tone words (ruthless, sugarcoat, trash, bulletproof). v1 kept in version-history; status set to needs-retest.

## [2026-10-18] rewrite | create-fictionalized-caselet.md
Rewrote with the asd-ste100 and structured profiles. Kept `<industry>`, `<product>`, `<product-dilemma>`, the four register names, and the empty tags at the end. v1 kept in version-history; status set to needs-retest.

## [2026-10-18] rewrite | generate-ai-prompt-library-for-pms.md
Rewrote with the asd-ste100 and structured profiles. The `<prompt-elements>` definitions were copied unchanged. The citation vs "do not include references" contradiction was left as is. v1 kept in version-history; status set to needs-retest.

## [2026-10-18] rewrite | ai-powered-discovery-analysis-synthesis-user-prompt.md
Rewrote with the asd-ste100 and structured profiles. The nine bracketed fields are unchanged. v1 kept in version-history; status set to needs-retest.

## [2026-10-18] rewrite | ai-powered-discovery-analysis-synthesis-system-prompt.md
Rewrote with the asd-ste100 and structured profiles. All rules, numbers, the GOOD/BAD example, the 11-stage sequence, and the progress tracker were kept; sentences were rewritten. v1 kept in version-history; status set to needs-retest.

## [2026-10-18] fix | prompt-build leverages the Obsidian skills
Audit of `prompt-build` against `obsidian-markdown`, `obsidian-bases`, `json-canvas`, and `obsidian-cli`. (1) `build.py` now strips private `%%comments%%` (outside code fences) before embedding data; the old page showed them. (2) Created `system/library.base` (4 views) and verified it with `obsidian base:query`. (3) `build.py` now maintains `system/chains.canvas`, add-only and validated. (4) The page renderer now resolves aliases and renders tables, italics, highlights, nested lists, footnotes, rules, block IDs, and embeds. (5) `SKILL.md` rewritten; tests added under `.claude/skills/prompt-build/tests/`.

## [2026-10-18] status | all 9 prompts set to verified
The user retested all nine prompts, so `status` was changed from `needs-retest` to `verified` directly in each note's frontmatter. Version, dates, and prompt text were not changed.

## [2026-10-22] create | prompt-find skill
Added `.claude/skills/prompt-find/` (`SKILL.md`, `find.py`, tests). Read-only search over `prompts/` with weighted matching, synonym groups, STRONG/WEAK fit labels, filters, `--show` for the copy-ready block, and `--set` to fill placeholders. Found and fixed one bug during testing: a wrapper-tag fill-in could swallow the text between an inline `<tag>` and a distant closing tag.

## [2026-10-22] create | prompt-lint skill
Added `.claude/skills/prompt-lint/` (`SKILL.md`, `lint.py`, 31 tests). 40+ checks across schema, links, duplicates, tags, staleness, index drift, and generated outputs; `--fix-index` rewrites `system/index.md`. First run on the library: 0 errors, 1 warning (tags `persona`/`personas`), 3 notes. Also fixed `build.py`: `load_categories` treated the `|---|` table row as a category.

## [2026-10-22] fix | page fill-in leaves no stray closing tag
Ported the wrapper-aware fill-in from `prompt-find` (`fill()`) into the page (`fillPrompt` in `prompt-build/template.html`). Browser check: for every prompt with variables the page's filled text equals `find.py --show --set` output, with balanced tags and no lost text. Added 7 tests to `tests/test_renderer.js`.

## [2026-10-22] create | README.md
Added `README.md` at the vault root: what the vault is, the raw → curated → prompts → system flow, daily use, the five skills, the note format, generated outputs, rules, setup, maintenance, and limits.

## [2026-10-22] fix | source link cleaned before publishing
Removed the share-tracking parameters (`utm_source`, `utm_medium`, `rcm`) from `source` in `market-research-analysis-with-ai.md`; the post link itself is unchanged. Page rebuilt.

## [2026-10-22] ingest | costars-prompt-generator.md
Source `curated/COSTARS Prompt Generator.md`. Prompt block copied exactly, including its 15 invisible U+FEFF characters. The example's `{{PRODUCT_IDEA}}` and `{{TARGET_CUSTOMER}}` are listed as variables (user's choice).

## [2026-10-22] ingest | customer-interview-questions-generator.md
Source `curated/Customer Interview Questions Generator.md`. Prompt block copied exactly. `{{USER_CONTEXT}}` and `{{INTERVIEW_OBJECTIVE}}` listed as variables.

## [2026-10-22] ingest | grill-me.md
Source `curated/grill-me.md`. Prompt block copied exactly. A longer standalone prompt, different from the `grill-me` Claude Code skill.

## [2026-10-22] ingest | interactive-clarity-prompt.md
Source `curated/Interactive Clarity Prompt.md`. Prompt block copied exactly. `[ROLE]` listed as a variable.

## [2026-10-22] ingest | interactive-concept-note-generator.md
Source `curated/Interactive Concept Note Generator.md`. Prompt block copied exactly. Written for the Institute of Product Leadership; the note says so.

## [2026-10-22] ingest | pm-workflow-for-artefact.md
Source `curated/PM Workflow for Artefact.md`. Prompt block copied exactly. The source description's typo ("Pa Product Manager") was tidied in `use-case` only.

## [2026-10-22] cleanup | six curated sources moved to trash
After the user confirmed, moved to Obsidian's trash (recoverable): `COSTARS Prompt Generator.md`, `Customer Interview Questions Generator.md`, `grill-me.md`, `Interactive Clarity Prompt.md`, `Interactive Concept Note Generator.md`, `PM Workflow for Artefact.md`. Each prompt block had been verified identical to its source before deletion.

## [2026-10-22] rewrite | pm-workflow-for-artefact.md
Rewrote with the asd-ste100 and structured profiles. Folded the Checklist and Instructions sections into Task, Input, and numbered Steps, merged Verbosity into Constraints, and left the worked example unchanged. v1 kept in version-history; status set to needs-retest.

## [2026-10-22] rewrite | customer-interview-questions-generator.md
Rewrote with the asd-ste100 and structured profiles. Kept `{{USER_CONTEXT}}`, `{{INTERVIEW_OBJECTIVE}}`, and the `<interview_script>` tags; moved the avoid-leading-questions rules into a Constraints section before the Steps. v1 kept in version-history; status set to needs-retest.

## [2026-10-22] rewrite | grill-me.md
Rewrote with the asd-ste100 and structured profiles. Sentence-level edits only: 182 of 211 lines unchanged; the final-summary headings, key questions, quoted phrases, and labels are unchanged. v1 kept in version-history; status set to needs-retest.

## [2026-10-22] change | the page shows public prompts only, without version history
(1) `build.py` no longer puts `## version-history` on the page: it shows only the latest version, and the page is about a third smaller. (2) New note property `visibility` (`public` | `private`). The page shows only `public` prompts; a note without it, or with another value, is treated as private and left off. Links to non-public prompts are scrubbed from public prompts' page data so hidden names cannot leak. All 15 existing prompts were set to `visibility: public` (user's choice) and new prompts default to public. `visibility` controls the page only: private notes stay readable in the Git repository. Also updated: `schema.md`, `prompt-ingest`, `prompt-lint` (`missing-visibility`, `bad-visibility`, `private-in-repo`), the Base (visibility column, "Not public" view), README, and `CLAUDE.md`.
