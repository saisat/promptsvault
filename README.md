# PromptsVault

A personal **AI prompt library** kept as an Obsidian vault. You capture prompts, test them, and drop the good ones into a folder. Claude Code skills then turn each one into a clean, categorised note, and keep a searchable index, a one-page reader, a live table and a chain map up to date.

It follows the [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): you curate the sources, an LLM does the bookkeeping, and a short rulebook ([`CLAUDE.md`](CLAUDE.md)) keeps it disciplined. Here the "wiki" is a library of atomic, copy-ready prompts instead of essays.

## How a prompt moves through the vault

```
raw/  ──you test it──▶  curated/  ──ingest──▶  prompts/  ──build──▶  system/
capture                 tested, yours           finished notes       page, Base, canvas
(untested)              (input)                 (the library)        (generated)
```

| Folder | Who owns it | What goes in it | What Claude may do |
|---|---|---|---|
| `raw/` | you | Untested prompts from anywhere: articles, posts, ideas | **Nothing. Claude never reads, lists, or touches it.** |
| `curated/` | you | Prompts you have tested, in any format, with optional notes | Read only. You delete files after ingest. |
| `prompts/` | the skills | One finished note per prompt: the prompt, usage notes, examples, links, version history | Read and write. This is the single source of truth. |
| `system/` | the skills | `index.md`, `log.md`, `prompt-library.html`, `library.base`, `chains.canvas`, plus the shared rules `schema.md` and `taxonomy.md` | Read and write |

## Daily use

You can type the slash command or just ask in plain words.

1. **Capture** a prompt into `raw/`. Any format, however you like.
2. **Test it** in your AI tool of choice.
3. **Promote it.** If it works, move the file into `curated/`. Put your own usage notes or examples in the same file if you have them.
4. **Ingest.** Say *"ingest the prompts in curated"* (`/prompt-ingest`). Claude creates a clean note in `prompts/`, shows it, and waits for your approval. At the end it offers to move the source file to the trash. It never deletes without your yes.
5. **Rebuild the page.** Say *"build"* (`/prompt-build`), then open `system/prompt-library.html`.
6. **Find a prompt.** Ask *"which prompt should I use to stress-test a plan?"* (`/prompt-find`). You get the best match, why it fits, and the prompt ready to paste.
7. **Improve a prompt.** `/prompt-rewrite` rewrites a note's prompt in a named style. Retest it afterwards.
8. **Check the library.** `/prompt-lint` finds broken links, schema mistakes, duplicates and out-of-date files.

## The skills

| Skill | What it does | What it changes |
|---|---|---|
| `prompt-ingest` | Turns a file in `curated/` into a schema-conformant note in `prompts/`: frontmatter, category, tags, variables, related links. Updates the index and log. Re-ingesting an improved prompt keeps the old text in version history. | Creates notes in `prompts/`, `system/index.md`, `system/log.md`. Never edits the prompt text or your source file. |
| `prompt-rewrite` | Rewrites a prompt with one or more profiles: `asd-ste100` (Simplified Technical English), `structured` (labelled sections), `concise`. Shows a before/after first. | The prompt text only, and it saves the old text in `## version-history` and sets `status: needs-retest`. It is the only skill allowed to change prompt text. |
| `prompt-build` | Builds the one-page reader and the chain canvas. Maintains the live Base. | `system/prompt-library.html`, `system/chains.canvas`. Never touches `prompts/`. |
| `prompt-find` | Searches `prompts/` by meaning and keywords, labels each match STRONG or WEAK, prints a copy-ready block, and can fill in placeholders. | Nothing. Read-only. |
| `prompt-lint` | Health check: 40+ checks, then proposes metadata fixes. `--fix-index` rewrites the index. | Nothing by default. Fixes only metadata, and only with your approval. |

## What a prompt note looks like

One file per prompt, named in kebab-case, e.g. `prompts/be-my-ruthless-mentor.md`.

```markdown
---
type: prompt
title: Be my ruthless mentor
aliases: [Be my ruthless mentor]
category: thinking-partner      # one value from system/taxonomy.md
tags: [critique, anti-sycophancy, persona]
status: verified                # verified | needs-retest | retired
visibility: public              # public | private; only public prompts appear on the web page
models-tested: []
source: own                     # a URL, an author, or "own"
variables: []                   # placeholders you fill in, e.g. ["<industry>"]
use-case: Avoid model sycophancy by getting blunt, no-flattery critique of an idea.
related: []                     # links to similar prompts
next: []                        # links to prompts that follow this one in a chain
created: 2026-10-18
updated: 2026-10-18
version: 2
---

## prompt
(exactly one fenced code block: the thing you copy)

## when-to-use / notes / examples / related / version-history
```

The full definition is in [`system/schema.md`](system/schema.md). The allowed categories are in [`system/taxonomy.md`](system/taxonomy.md). Edit that file to add a category, and the skills will accept it.

**Visibility.** `public` prompts appear on the web page. `private` prompts, and notes with no `visibility`, do not. New prompts default to `public`. This controls the **page only**: a private prompt is still readable in the Git repository and its history if the repository is public.

**Status values.** `verified` means you tested it and it works. `needs-retest` means the text changed since the last test (a rewrite sets this). `retired` means don't use it. After you retest, set the status yourself, or ask Claude to.

## The generated outputs

- **`system/prompt-library.html`**: the one-page reader, also published at **https://saisat.github.io/promptsvault/**. Locally, open it with `open system/prompt-library.html`. It shows only `public` prompts and only their latest version (no version history). It works offline and has search (press `/`), filters by category, status and tag, a copy button on every prompt, fill-in boxes for placeholders, wikilinks between prompts, dark mode, and a phone layout. It is regenerated each build, so never edit it by hand.
- **`system/library.base`**: an Obsidian Base with five live views: All prompts, By category, Needs retest, Not public, and Recently updated. It updates by itself.
- **`system/chains.canvas`**: an Obsidian canvas of prompts that follow each other (`next` links). Rebuilds only add to it, so layout changes you make by hand are kept.
- **`system/index.md`** and **`system/log.md`**: a catalog of every prompt by category, and an append-only record of what the skills did.

## Rules the skills follow

- **`raw/` is off limits.** Claude never reads, lists or edits it.
- **Only `prompt-rewrite` changes prompt text.** Every other skill leaves it exactly as written.
- **Nothing is deleted without your confirmation.**
- **You approve edits.** Claude shows what it will change first.
- **Everything is kebab-case**: file and folder names, categories, tags, status values. The conventional files `README.md`, `CLAUDE.md` and `SKILL.md` are the exceptions.
- **New categories need your say-so.** A skill proposes one and waits.

## Setup

Needed:
- [Obsidian](https://obsidian.md) with this folder opened as a vault.
- [Claude Code](https://claude.com/claude-code), started from the vault folder, so it picks up `CLAUDE.md` and `.claude/skills/`.
- Python 3 (builds, search and lint use only the standard library).
- The Obsidian skills (Markdown, Bases, canvas and CLI rules), installed once for your user:
  ```
  npx skills add https://github.com/kepano/obsidian-skills -g
  ```
- Optional: Node.js to run the page tests. The Obsidian CLI also works, but only while the Obsidian app is open.

## Version control (Git and GitHub)

The vault is a Git repository, published on GitHub as `promptsvault`.

- **Not in Git:** `raw/` and `curated/` are listed in [`.gitignore`](.gitignore). Your captures and untested prompts stay on your machine only. Also ignored: Obsidian's own settings folder (`.obsidian/`), `.claude/settings.local.json`, and OS and Python noise.
- **In Git:** the library (`prompts/`), the generated outputs and shared rules (`system/`), the skills and their tests (`.claude/skills/`), `CLAUDE.md`, and this file.
- **After cloning on a new machine:** create the two ignored folders and rebuild the page.
  ```
  mkdir raw curated
  ```
  then open the folder as a vault in Obsidian, which creates its own `.obsidian/` settings, and run `/prompt-build`. Install the Obsidian skills as described under Setup.
- **Committing:** a good rhythm is one commit after each ingest, rewrite or lint fix, for example `git add -A && git commit -m "Ingest: <prompt name>"`. Git cannot see `raw/` or `curated/`, so `git add -A` is safe.
- **The live page.** [`.github/workflows/pages.yml`](.github/workflows/pages.yml) builds the reader from `prompts/` and publishes it with GitHub Pages at https://saisat.github.io/promptsvault/. It runs on every push to `main` that changes `prompts/`, `system/taxonomy.md`, or the `prompt-build` skill, so the live page always matches the library, even if your local copy of the page is out of date. To redeploy by hand, open the repository's Actions tab, choose "Publish the prompt library page", and click Run workflow. In Settings → Pages the source must stay set to "GitHub Actions". Only the page is published as a website, and only `public` prompts are on it. The notes themselves, including `private` ones, are still readable in the repository.
- **Before publishing anything new**, check `source` links for tracking parameters (`utm_…`, `rcm=…`). Share links copied from phones often carry an identifier. `prompt-lint` does not check this yet.
- The vault lives in iCloud Drive and the `.git` folder is inside it. If iCloud ever reports conflicted copies inside `.git`, move the repository's Git data out of iCloud with `git init --separate-git-dir <path>`.

## Keeping it healthy

- Run `/prompt-lint` after you add or change several notes. It catches problems early, such as a `next` link to a note that no longer exists.
- If the page looks out of date, run `/prompt-build`. Lint tells you when it is stale.
- Run the tests after changing a skill:
  ```
  cd .claude/skills/prompt-lint  && python3 -I tests/test_lint.py
  cd .claude/skills/prompt-find  && python3 -I tests/test_find.py
  cd .claude/skills/prompt-build && python3 -I tests/test_build.py && node tests/test_renderer.js
  ```
- **Base shows old numbers right after an edit?** Give Obsidian a few seconds to re-index.
- **Obsidian CLI says "unable to find Obsidian"?** Open the app. The skills fall back to plain file access when they can.

## Limits to know about

- **Search is keywords plus a small synonym list, not true semantic search.** `prompt-find` relies on Claude to add synonyms and judge the fit. It will say so when a match is only weak.
- **Whether a prompt is good is up to you.** The skills check structure, not model behaviour. `models-tested` is filled in by hand.
- **Re-ingesting an improved prompt is designed but not yet exercised.** First ingests, rewrites, search, lint and builds have all been run. Check the diff carefully the first time you re-ingest.
- **The page does not render** math, Mermaid diagrams, inline `#tags`, inline footnotes, or image and file embeds. Embeds show as a link or `↪ name`.

## Where things live

```
PromptsVault/
├── README.md             this file
├── CLAUDE.md             the rulebook Claude reads at the start of each session
├── raw/                  your untested captures (Claude never touches this; not in Git)
├── curated/              your tested prompts, waiting to be ingested (not in Git)
├── prompts/              the library: one note per prompt
├── system/               generated files and the shared definitions
└── .claude/skills/       prompt-ingest, prompt-rewrite, prompt-build, prompt-find, prompt-lint
```
