# Prompt library vault

A personal AI prompt library, run on the LLM Wiki pattern: human-curated sources, an LLM-maintained layer, and skills that do the bookkeeping.

## Layers
| Folder | Owner | Contents | Claude may |
|---|---|---|---|
| `raw/` | user | untested captures from the internet and elsewhere | **never read, list, edit, or move anything here** |
| `curated/` | user | prompts after the user's testing, optionally with notes. Free-form input to ingest | read only. The user deletes files after ingest. |
| `prompts/` | `prompt-ingest` | the finished library: one note per prompt, with notes, related links, and version history | read and write. The source for every other skill. |
| `system/` | skills | `index.md`, `log.md`, `library.base`, `chains.canvas`, `prompt-library.html`, plus the shared definitions `schema.md` and `taxonomy.md` | read and write |

Flow: `raw/` (user tests) → `curated/` (`prompt-ingest`) → `prompts/` → `prompt-build` → `system/`.

## Rules
- Use kebab-case for all file and folder names, categories, tags, and status values (e.g. `market-research`, `needs-retest`).
- Write notes in Obsidian Flavored Markdown (`obsidian-markdown` skill), `.base` files with `obsidian-bases`, and `.canvas` files with `json-canvas`. `obsidian-cli` is optional and needs the Obsidian app running.
- One prompt per note. The prompt, usage notes, examples, and links all live in that note.
- Only `prompt-rewrite` may change the text of a prompt in `prompts/`. `prompt-ingest` copies the prompt text from `curated/` exactly and never edits `curated/` files.
- Nothing is deleted without the user confirming it.
- `raw/` and `curated/` are git-ignored (see `.gitignore`). Never stage or commit them, never use `git add -f` on them, and never remove them from `.gitignore`. Do not commit or push unless the user asks.
- Only prompts with `visibility: public` appear on the generated web page. New notes get `visibility: public` by default. `visibility` does not hide a note from the Git repository, so never describe `private` as "not on GitHub".
- Do not add a category that is not in `system/taxonomy.md`. Propose it to the user instead.
- The user approves edits manually. Do not batch-apply changes without showing them.

## Skills (`.claude/skills/`)
`prompt-ingest` (curated → prompts), `prompt-rewrite`, `prompt-build`, `prompt-find` (read-only search of `prompts/`), `prompt-lint` (health check; fixes metadata only, with approval).
