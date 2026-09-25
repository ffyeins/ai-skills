---
name: doc-lookup
description: Local, version-checked documentation for tmux, Neovim (Lua API,
  keymaps, LSP, lazy.nvim, kickstart.nvim), Bash, and the Java 8 API. Use it
  before answering any question about these tools' options, defaults, key
  bindings, config syntax, or API signatures, even when the answer seems
  familiar, because defaults and APIs change between versions. For
  documentation lookups on any other developer tool, check here first, then
  fall back to web search.
compatibility: Requires python3 for the DevDocs API references.
---

# Documentation Lookup

Check the local knowledge base bundled with this skill before searching online.
Paths below are relative to this skill's folder.

It has two sources:

- `docs/`: curated markdown guides grouped by category (e.g. `docs/tools/`),
  each category with an `_index.md` routing table.
- `devdocs/`: full API references downloaded from DevDocs, one folder per
  topic, read with `scripts/devdocs.py`.

## Lookup procedure

### Step 1: Find what's available

List the category folders under `docs/`, and run `scripts/devdocs.py topics`
to list the DevDocs topics and their versions. `devdocs/` isn't in version
control, so it may be missing or empty; if so, skip step 3.

If nothing local covers the topic, go to step 4.

### Step 2: Search curated docs

1. Read `docs/<category>/_index.md` to find the right topic file.
2. Read only the topic files you need. Each starts with the version it was
   verified against and a contents list; in long files, use the list to go
   straight to the relevant section.

### Step 3: Search DevDocs

1. Find entries whose name contains the term (case-insensitive), best matches
   first:

   ```sh
   scripts/devdocs.py search <topic> <term>
   ```

   Each result line is the entry name, its path, and its type, separated by
   tabs. The path looks like `<page>#<section>`, e.g.
   `bourne-shell-builtins#index-getopts`.

2. Print that entry as plain text:

   ```sh
   scripts/devdocs.py show <topic> <path>
   ```

   With a `#section` it prints only that entry; without one, the whole page.
   Output stops after 300 lines; add `--max-lines 0` to see the rest.

### Step 4: Fall back to online search

Search online only if no local source covers the topic, or the local docs
don't fully answer the question. When you do, tell the user the topic wasn't
found locally, or that the local docs were incomplete.

## Versions

When the answer depends on a version, such as a default value or a flag that
only some releases have, tell the user which version the local docs describe.
Curated guides state it at the top, and `scripts/devdocs.py topics` shows it
for DevDocs. If it may differ from what the user runs, say so.
