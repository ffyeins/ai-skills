# tools

Maintenance scripts for the humans who look after this repo. Agents never run
these; they aren't part of any skill.

## download-devdocs.sh

Downloads a [DevDocs](https://devdocs.io) topic into
`skills/doc-lookup/devdocs/`. That folder is gitignored because the data is
large (Java 8 alone is 34 MB), so run this on each new machine for every topic
you want:

```sh
tools/download-devdocs.sh bash
tools/download-devdocs.sh openjdk~8
```

Slugs come from the `slug` field in <https://devdocs.io/docs.json>, and the
script checks the slug there before downloading anything. The folder name
swaps `~` for `-`. The script needs `curl` and `jq`; the skill itself only
needs `python3`.

Each topic folder also gets a `meta.json` with the DevDocs name, release, and
download date. The skill's `scripts/devdocs.py topics` shows it, so agents can
say which version they're quoting. Topics downloaded before `meta.json`
existed show "version not recorded" until you download them again.

After adding a topic, add it to the `description` in
`skills/doc-lookup/SKILL.md` so agents know it's covered.

## Adding curated docs to doc-lookup

1. Create or pick a category folder under `skills/doc-lookup/docs/`
   (e.g. `docs/tools/`). A new category needs its own `_index.md`.
2. Add the topic file (under ~500 lines). It starts with a `# Title`, a
   one-line `> summary`, a `Verified against:` line naming the tool version and
   the month, and a **Contents** list of its `##` sections.
3. Add a row to that category's `_index.md`: file, topic, when to read.
4. If it's a new subject, mention it in the skill's `description`.
