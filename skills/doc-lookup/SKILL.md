---
name: doc-lookup
description: Local documentation knowledge base to check before searching the
  web. Covers tmux (sessions, panes, key bindings, scripting, config), Neovim
  (Lua API, keymaps, LSP, lazy.nvim plugins, kickstart.nvim), Bash builtins and
  syntax, and the Java 8 (OpenJDK) API. Use whenever looking up documentation,
  API references, command options, or config syntax for these or any other
  developer tool, language, or framework — check here first, then fall back to
  online search.
compatibility: Requires jq for the DevDocs API references.
---

# Documentation Lookup

Check the local knowledge base bundled with this skill before searching online.
It has two sources:

- `docs/`: curated markdown guides grouped by category (e.g. `docs/tools/`),
  each category with an `_index.md` routing table.
- `devdocs/`: API references downloaded from DevDocs, one folder per topic.

All paths below are relative to this skill's folder.

## Lookup procedure

### Step 1: Find what's available

List the category folders under `docs/` and the topic folders under
`devdocs/`. `devdocs/` isn't in version control, so it may be missing or empty;
if so, skip step 3.

If nothing local covers the topic, go to step 4.

### Step 2: Search curated docs

1. Read `docs/<category>/_index.md` to find the right topic file.
2. Read only the topic files you need. Each starts with a contents list; in
   long files, use it to go straight to the relevant section.

### Step 3: Search DevDocs

1. Find entries whose name contains the term (case-insensitive):

   ```sh
   jq -r --arg q '<term>' '.entries[] | select(.name | ascii_downcase | contains($q | ascii_downcase)) | "\(.name)\t\(.path)"' devdocs/<topic>/index.json
   ```

   Each result's path looks like `<page>#<section>`, e.g.
   `bourne-shell-builtins#index-getopts`.

2. Extract the page as plain text, using only the part **before** `#`
   (`db.json` is keyed by page; the full path returns nothing):

   ```sh
   jq -r --arg p '<page>' '.[$p]' devdocs/<topic>/db.json | sed 's/<[^>]*>//g'
   ```

   Pages can be long (a whole Java class). Search the output for the entry
   name, e.g. with `grep -n -A20 '<term>'`, rather than reading all of it.

### Step 4: Fall back to online search

Search online only if no local source covers the topic, or the local docs
don't fully answer the question. When you do, tell the user the topic wasn't
found locally, or that the local docs were incomplete.
