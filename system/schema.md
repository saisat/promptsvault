# Note schema

Every note in `prompts/` follows this shape. Filenames are kebab-case (`be-my-ruthless-mentor.md`). Files in `curated/` are free-form input to `prompt-ingest` and don't need to follow it.

## Frontmatter

```yaml
---
type: prompt
title: Be my ruthless mentor
aliases: [Be my ruthless mentor] # the title, so [[Be my ruthless mentor]] and link suggestions find the kebab-case file
category: thinking-partner      # exactly one value from taxonomy.md
tags: [critique, sycophancy]    # kebab-case, free-form
status: verified                # verified | needs-retest | retired
visibility: public                # public | private; only public prompts appear on the web page
models-tested: [claude-opus-4]  # models the prompt was tried on
source: own                     # a URL, an author, or "own"
variables: []                   # placeholders found in the prompt, e.g. ["<industry>"]
use-case: One line saying when to reach for this prompt.
related: []                     # wikilinks to similar prompts, e.g. ["[[other-prompt]]"]
next: []                        # wikilinks to prompts that follow this one in a chain
created: 2026-10-18
updated: 2026-10-18
version: 1
---
```

## Body

```markdown
## prompt

(exactly one fenced code block, the copy target)

## when-to-use
## notes
## examples
## related
## version-history
```

- `## prompt` holds one fenced block and nothing else except an optional one-line lead-in.
- `## related` repeats `related` and `next` as readable wikilinks with a short reason each.
- `## version-history` lists older prompt text newest first, each under `### v<n> (<date>, <reason>)`.
- Wikilinks use the note filename without extension: `[[be-my-ruthless-mentor]]`.
- `visibility` controls the generated web page only. A note without it, or with any value other than `public`, is left off the page. It does not hide the note from the Git repository, so a `private` prompt is still readable on GitHub. The page never shows `## version-history`: it shows the latest version only.
- Write notes in Obsidian Flavored Markdown, following the `obsidian-markdown` skill: wikilinks for vault notes, standard links only for external URLs, properties as valid YAML, and callouts (`> [!warning]`) for cautions inside `## notes`.
- Link properties (`related`, `next`) hold quoted wikilinks so Obsidian reads them as links. Obsidian rewrites them as a block list when edited in its UI; both forms are valid.
