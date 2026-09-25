# Skill authoring guide

How to write skills in this repo so they trigger reliably, stay small, and work
the same in Claude Code, GitHub Copilot, and OpenAI Codex.

This guide holds the rules. Details about individual agents that change often,
such as skill folders, which fields each agent reads, and listing budgets, live
in [agent-support.md](agent-support.md) with their sources and the date they
were last checked.

## Contents

1. [How skills load](#1-how-skills-load)
2. [When to write a skill](#2-when-to-write-a-skill)
3. [Portability](#3-portability)
4. [Naming](#4-naming)
5. [Description](#5-description)
6. [Body](#6-body)
7. [Bundled files](#7-bundled-files)
8. [Testing](#8-testing)
9. [Security and hygiene](#9-security-and-hygiene)
10. [Installing](#10-installing)
11. [Checklist](#11-checklist)

---

## 1. How skills load

Every agent loads a skill in three stages:

| Stage | What loads | When | Cost |
|---|---|---|---|
| 1. Metadata | `name` + `description` | Always, for every installed skill | ~100 tokens per skill, all the time |
| 2. Body | The rest of `SKILL.md` | When the agent decides the skill is relevant | Up to a few thousand tokens, and it stays for the rest of the session |
| 3. Resources | Files in `references/`, `scripts/`, `assets/` | Only when the body tells the agent to open or run them | Only what's used |

Three consequences shape everything below:

- **The description is the trigger.** The agent chooses skills from stage 1
  alone. A vague description means the skill never loads, however good the body.
- **Descriptions get cut.** Agents cap how much listing text they show. Claude
  Code cuts long descriptions, and Codex shortens them, then drops whole skills,
  once the list outgrows its budget. Whatever comes first in the description is
  what survives.
- **The body competes for context, turn after turn.** Once loaded, every line
  sits next to the user's conversation and code for the rest of the session.
  Put only what's needed every time in the body, and move the rest into files
  the agent opens on demand.

## 2. When to write a skill

Write a skill when you keep pasting the same instructions, checklist, or
multi-step procedure into chat, or when a section of `AGENTS.md` has grown from
a fact into a procedure.

Put it somewhere else when it is:

| It is… | Put it in |
|---|---|
| A fact or rule that applies to every task in a repo | `AGENTS.md` (or `CLAUDE.md`) |
| Access to a live system: an API, a database, an issue tracker | An MCP server, or a CLI the agent can run |
| A one-off request | The prompt |

Before adding a skill, check what's already installed, including skills from
plugins or synced from an account. Every skill costs listing tokens in every
session, and two skills with overlapping descriptions make the agent pick the
wrong one. Prefer extending or narrowing an existing skill over adding a
neighbor.

## 3. Portability

The shared [Agent Skills](https://agentskills.io/specification) format covers
everything a skill needs. Each agent adds its own extras on top, and other
agents ignore them or show them as plain text. **Write only to the shared
format, unless an extra is harmless when ignored.**

In short, Claude Code reads `~/.claude/skills/`, Codex reads `~/.agents/skills/`,
and Copilot reads both, plus `~/.copilot/skills/`.
[agent-support.md](agent-support.md) has the details. This repo keeps
`AGENTS.md` as its rules file and `CLAUDE.md` as a symlink to it.

### Frontmatter

Always include:

```yaml
---
name: skill-name
description: What it does. Use when ...
---
```

Optional fields from the shared format, fine to use anywhere:

- `license`: e.g. `MIT`, if the skill might be shared.
- `compatibility`: requirements outside the skill, at most 500 characters, e.g.
  `Requires python3 and network access`. Omit it if there are none.
- `metadata`: string keys with string values. Quote values that look like
  numbers or booleans: `version: "1.0"`, not `version: 1.0`.

Agent-specific fields are **off by default**. The common ones:

| Field | Why it's off |
|---|---|
| `when_to_use` | Only Claude Code reads it. Put all trigger text in `description` |
| `allowed-tools` | Tool names differ per agent |
| `argument-hint`, `user-invocable` | They only affect the slash-command menu |
| `context`, `agent`, `model`, `effort`, `hooks`, `paths`, `arguments` | Claude Code behavior with no equivalent elsewhere |

Use one only when you can say why in a YAML comment next to it, and when the
skill still behaves correctly in an agent that ignores it. The one standing
exception is the manual-only setup below.

**Keep the YAML plain.** A description can run over several indented lines as
a plain value. Wrap it in double quotes if it contains `: ` or ` #`, or starts
with a character YAML treats specially: `[ { * & ! | > ' " % @` or a backtick.
Never use a `|` block, because it keeps the line breaks.

**Have exactly one `SKILL.md` per skill folder.** Give supporting files other
names, such as `references/forms.md`. Some uploaders reject a folder that
contains two.

### Skills that must not start on their own

A skill that deploys, deletes, or sends messages must run only when the user
asks. No single switch works in every agent, so use all four layers:

1. `disable-model-invocation: true` in the frontmatter, with a reason comment,
   for Claude Code and VS Code.
2. `agents/openai.yaml` in the skill folder, for Codex:

   ```yaml
   policy:
     allow_implicit_invocation: false
   ```

3. A description that begins "Only when the user explicitly asks to…".
4. A first step in the body that confirms with the user before doing anything.

The first two stop the agents that support them. The last two cover every other
agent, including any that gains skill support later.

### Body

| Don't write | Why | Write instead |
|---|---|---|
| "Use the Read tool on `references/api.md`" | Tool names differ per agent | "Read `references/api.md`" |
| "Run it with the Bash tool" | Same | "Run `scripts/check.sh`" |
| `$ARGUMENTS`, `$0`–`$9`, `${CLAUDE_SKILL_DIR}` | Claude Code replaces these before the model reads the file; other agents show them as written | "The user supplies a file path; if they didn't, ask for one" |
| Shell code that uses `$1`, `$0`, … | Claude Code rewrites it too, even inside code blocks: when the skill is given arguments, `awk '{print $1}'` ends up printing the second argument | Put the code in `scripts/` or a reference file, which are never rewritten |
| `` !`git status` ``, or a code block fenced with ```` ```! ```` | Claude Code runs it when the skill loads and pastes in the output; others print it | "Run `git status` first" |
| An MCP tool's name | Which MCP servers exist, and what their tools are called, differs per machine and agent | Name the job ("create an issue in the tracker"), and list the dependency in `compatibility` |
| "Spawn a subagent to…" | Not every agent has subagents | Describe the work; let the agent decide how |
| "The user invoked `/skill-name`" | Skills also start automatically, and Codex uses `$skill-name` | Handle both ways of starting |

Also keep `!` from sitting directly before a backtick anywhere in `SKILL.md`.
Claude Code treats `` !`…` `` at the start of a line or after a space as a
command to run.

### Paths

- Write every path relative to the skill folder: `references/api.md`, not
  `/Users/…/ai-skills/skills/x/references/api.md`.
- Use forward slashes.
- Don't reference anything outside the skill folder, including other skills or
  this repo's `docs/`. The skill is used through a symlink, so it can't assume
  where it lives or what's next to it.
- Agents run commands from the user's project, not from the skill folder. In
  any `SKILL.md` that runs commands or opens files, say once near the top:
  "Paths below are relative to this skill's folder." The agent knows where the
  skill lives and resolves paths from there.

### Scripts

- Use POSIX `sh` or `python3` with only the standard library. If a script needs
  anything else, say so in `compatibility` and in the body.
- Make them executable (`chmod +x`) with a shebang line.
- Resolve files from the script's own location, not the current directory.
  These lines belong in the script, never in `SKILL.md`:
  - sh: `dir="$(cd "$(dirname "$0")" && pwd)"`
  - python: `Path(__file__).resolve().parent`
- Assume they may run on macOS or Linux, so avoid GNU-only flags and commands
  (`sed -i ''` vs `sed -i`, `date -d`, `timeout`, …).
- Some agents run commands in a sandbox with no network and no writes outside
  the workspace. Say which steps need either, and what to tell the user if they
  are blocked.

## 4. Naming

- Lowercase letters, digits, and single hyphens, 1–64 chars:
  `^[a-z0-9]+(-[a-z0-9]+)*$`.
- Must match the folder name exactly.
- Don't use `claude` or `anthropic`, which some agents reserve.
- Be specific: `openwrt-firewall`, `pdf-form-filling`. Avoid `helper`, `utils`,
  `tools`.
- Keep one pattern across the repo. Here that's noun phrases (`doc-lookup`,
  `pdf-form-filling`), not verb forms (`processing-pdfs`).
- Keep the name unique across everything installed on the machine, not just
  this repo. On a clash, Claude Code silently picks one (personal over project)
  and Codex lists both, so the wrong skill can run without warning.

## 5. Description

This is the most important line in the skill, so rewrite it until it's right.

**Rules**

- 1024 characters max, and under ~500 in practice. Aim for 1–3 sentences.
- Put the main use case in the first sentence. When the listing runs over
  budget, agents cut descriptions from the end.
- Third person ("Configures…", "Use when…"). It goes into the agent's system
  prompt, where "I" and "you" read wrong.
- State **what** the skill does and **when** to use it, all here. Nothing in
  the body can help the agent decide to load the skill.
- Include the words users actually type: file extensions, tool names, error
  messages, common phrasings.
- Say when, not how. Leave the steps to the body. An agent given a summary of
  the procedure sometimes follows the summary and never loads the body.
- Name close cases that should **not** trigger it when confusion is likely.
- No angle brackets (`<`, `>`); some agents treat the text as XML.
- Lean slightly assertive. Agents tend to skip skills more often than they
  overuse them, so "Use whenever…" beats "Can help with…".

**Examples**

Bad, which never triggers because it names nothing concrete:

```yaml
description: Helps with documents.
```

Bad, which says what but not when:

```yaml
description: A comprehensive toolkit for spreadsheet manipulation.
```

Bad, which spells out the steps instead of the trigger:

```yaml
description: Reads the router config, backs it up, edits the firewall zones,
  restarts the firewall service, then checks the logs.
```

Good:

```yaml
description: Configures OpenWrt routers through UCI — firewall4/nftables zones
  and rules, DHCP and DNS with dnsmasq, VLANs on DSA switches, WireGuard. Use
  whenever the user mentions OpenWrt, LuCI, uci commands, or /etc/config files,
  even if they don't say "OpenWrt". Not for generic Linux iptables or pfSense.
```

## 6. Body

**Assume the agent is smart.** Include only what it wouldn't already know or
would likely get wrong: your conventions, your environment, non-obvious steps,
known pitfalls. For each paragraph, ask whether the skill works worse without
it. If not, delete it. Don't repeat what `AGENTS.md` or the agent's own
instructions already say.

**Write instructions as commands.** Write "Run the tests" and "Read
`references/api.md`", not "The tests should be run" or "You might want to
read…".

**Explain why, briefly.** "Always sort by date, because reports are read
top-down by recency" works better than "ALWAYS sort by date!!!". Once the agent
knows the reason, it handles cases you didn't list. A clause is enough, because
a paragraph of backstory costs context on every turn.

**Match freedom to fragility.**

- Judgment tasks like reviewing, writing, or designing: give goals and
  criteria in prose.
- Tasks where there's a preferred way but some variation is fine: give a
  template or pseudocode.
- Fragile tasks like migrations, deploys, or exact file formats: give the exact
  command or script, and say "don't modify".

**Give a default, not a menu.** "Use `pdfplumber` for text extraction. For
scanned PDFs, use `pytesseract` instead." Don't list five libraries and let the
agent choose.

**Route early.** If the skill handles several jobs, say at the top which section
covers which: "Creating a new form? Follow *Create*. Filling in an existing
one? Skip to *Fill*."

**Write workflows as numbered steps.** For multi-step or risky tasks, add a
checklist the agent can copy and tick off, plus a validation loop:
*do → check → fix → check again*.

**Say what done looks like.** End with how to check the result: the command to
run, the file that must exist, or the output to compare against. That way the
agent knows when to stop.

**Give an exit.** Say what to do when the skill doesn't fit, because the input
isn't what it expects or its method fails. "If there's no `package.json`, tell
the user and stop" beats letting the agent improvise.

**Show, don't describe.** One concrete input → output example beats a paragraph
of rules, especially for formats like commit messages or report layouts.

**Stay consistent.** Pick one term per concept (e.g. always "endpoint", never a
mix of "URL", "route", and "path").

**Pin facts to versions, not dates.** Write "since Neovim 0.11", not "the new
API" or "as of 2026". If old behavior matters, put it under a clearly marked
"Legacy" heading.

**Suggested structure** (adapt it; don't pad sections you don't need):

```markdown
# Skill Title
One or two sentences: what this does and the core approach.
Paths below are relative to this skill's folder.

## When not to use          (only if the description can't cover it)
## Workflow                 (numbered steps, ending with a check)
## Examples                 (input → output)
## Reference files          (what each file holds and when to read it)
```

## 7. Bundled files

Keep `SKILL.md` under **500 lines** (roughly 5k tokens). Past that, split it.

```
skill-name/
  SKILL.md
  references/          # read on demand: API details, schemas, long guides
  scripts/             # run, don't read: deterministic or repetitive work
  assets/              # used in output: templates, boilerplate, images
  evals/               # test prompts (see Testing); agents never need them
  agents/openai.yaml   # only for manual-only skills (see Portability)
```

- **Link one level deep.** `SKILL.md` links to `references/x.md`. Reference
  files shouldn't send the agent on to more files, because agents often read
  nested links only partly.
  *Exception:* for large collections, a short `_index.md` that only routes
  (a table of file → topic → when to read) may sit between `SKILL.md` and the
  content files. Content files may point to their siblings, but every one must
  be listed in the index. See `skills/doc-lookup/`.
- **Say when to read each file**, not just that it exists:
  "Read `references/aws.md` only if the user deploys to AWS."
- **Split by variant** when a skill covers several frameworks or providers:
  one reference file each, so the agent reads only the one it needs.
- **Put a table of contents** at the top of any reference file over 100 lines.
- **Record the version a reference describes.** A reference file about a
  versioned tool starts with a line like `Verified against: tmux 3.7 (2026-09)`.
  When the tool moves on, you know which files to recheck. The agent, in turn,
  can warn when the user runs a different version.
- **Say whether to run or read each script.** "Run `scripts/validate.py
  out.json`" tells the agent to execute it, so only the output uses context.
  "See `scripts/validate.py` for the rules" tells it to read the source.
- **Turn repeated work into a script.** If testing shows the agent writing
  the same helper code every time, bundle it as a script.
- **Give large data a search script.** Don't make the agent type long `jq` or
  `grep` pipelines over big JSON dumps or logs. A script that takes a query and
  prints only the matching part is more reliable, and it keeps the output
  small.
- **Make scripts fail helpfully.** Print what went wrong and how to fix it,
  rather than a bare traceback. Explain constants
  (`TIMEOUT = 30  # slow networks`) instead of leaving magic numbers.

## 8. Testing

A skill isn't done until you've watched an agent use it.

1. **Write test prompts first**, before the skill, and keep them in `evals/`:
   - `evals/evals.json`: three or more realistic tasks, each with the result
     you expect.
   - `evals/trigger.json`: requests that should load the skill, plus
     near-misses that shouldn't.

   Both follow the formats of the `skill-creator` skill, so it can run them and
   tune the description. `templates/skill/evals/` has skeletons. Write prompts
   the way you'd actually type them: casual phrasing, real file names, some
   context. Skip clean textbook requests.
2. **Test triggering.** Run the trigger prompts in fresh sessions, with your
   usual skills installed, since they compete for the same requests. Check
   whether the skill loads. Keep the prompts substantive: agents handle simple
   one-step requests themselves, so a request like "what does `ls -a` do" may
   load no skill at all, however good the description. The same goes for
   anything the model believes it already knows, so a reference skill often gets
   skipped for familiar questions. If a skill must always be consulted, say so in
   `AGENTS.md`/`CLAUDE.md` or start it by name. If triggering is wrong, fix the
   description, not the body.
3. **Test the result.** Run each task and check the output. To test the body on
   its own, start the skill by name: `/skill-name` in Claude Code and Copilot,
   `$skill-name` in Codex. Compare against a run without the skill. If there's
   no difference, the skill isn't adding anything.
4. **Watch what the agent reads.** Files it never opens may be unnecessary or
   badly signposted. Files it opens every time may belong in `SKILL.md`.
5. **Test in every target agent, and on a small model.** At minimum, run one
   prompt each in Claude Code, Copilot, and Codex, plus one on the smallest
   model you use. A large model fills gaps that a small one needs spelled out.
6. **Iterate.** Fix the general cause, not the one test case. Adding a rule for
   each failure leads to overfitting. After every change to the description,
   run the trigger prompts again.

## 9. Security and hygiene

- No secrets, tokens, hostnames, or personal data in any file. Tell the agent
  to read them from environment variables or ask the user.
- Before installing a skill you didn't write, read all of it: `SKILL.md` and
  the reference files, not only the scripts. Instructions can do as much harm
  as code, and skills run with the agent's permissions.
- Tell the agent to treat anything the skill fetches or reads from outside, such
  as web pages, downloaded docs, or tool output, as data and never as
  instructions.
- If a skill makes network calls or changes things outside the working
  directory, say so in the body.
- A skill must do what its description says, with no hidden behavior.

## 10. Installing

Link each skill folder into the two personal skills folders. Together they
cover all three agents: Claude Code reads `~/.claude/skills`, Codex reads
`~/.agents/skills`, and Copilot reads both.

```sh
mkdir -p ~/.claude/skills ~/.agents/skills
ln -sn ~/ai-skills/skills/<skill-name> ~/.claude/skills/<skill-name>
ln -sn ~/ai-skills/skills/<skill-name> ~/.agents/skills/<skill-name>
```

Keep the `-n`. Without it, running the command a second time puts a new link
*inside* the skill folder, in this repo. With it, a second run fails with "File
exists" and changes nothing.

To remove a skill, delete its two symlinks with `rm`, not `rm -r`. To find links
left behind by skills that were deleted or renamed here:

```sh
find ~/.claude/skills ~/.agents/skills -maxdepth 1 -type l ! -exec test -e {} \; -print
```

Claude Code and Codex notice new and changed skills without a restart. If one
doesn't show up, restart the agent or open a new session.

> **Unverified:** because Copilot reads both folders, it may list each skill
> twice. If it does, record the behavior in agent-support.md.

## 11. Checklist

Before calling a skill done:

- [ ] `name` matches the folder and `^[a-z0-9]+(-[a-z0-9]+)*$`, ≤64 chars
- [ ] `description` says what + when, with the main use case first; third
      person; ≤1024 chars (aim for under ~500); no `<` `>`; no procedure
- [ ] Frontmatter is plain YAML: values quoted where needed, no `|` blocks,
      `metadata` values are strings
- [ ] No agent-specific frontmatter, or each field has a reason comment and is
      harmless if ignored
- [ ] Skills that must not start on their own use all four layers:
      `disable-model-invocation`, `agents/openai.yaml`, the description, and a
      confirmation step
- [ ] Body has no tool names, `$ARGUMENTS`, `$0`–`$9`, `${CLAUDE_…}`,
      `` !`cmd` ``, ```` ```! ```` blocks, or slash-command assumptions
- [ ] `SKILL.md` < 500 lines, written as instructions, ends with a way to check
      the result, and every paragraph earns its place
- [ ] If it runs commands or opens files, it says paths are relative to the
      skill folder; all paths are relative, use forward slashes, and stay
      inside the folder
- [ ] Reference files are linked one level deep (or through one routing
      index), each with "read when…"; files over 100 lines have a table of
      contents; versioned facts carry a `Verified against:` line
- [ ] Scripts are executable, POSIX `sh` or stdlib `python3`, resolve their
      own dir, and say when they need network or write outside the workspace
- [ ] No secrets or personal data, and no `TEMPLATE:` notes left
- [ ] Tested: `evals/` written; should- and should-not-trigger prompts
      checked; one real run in each of Claude Code, Copilot, and Codex

Quick checks, run from the skill folder:

```sh
wc -l SKILL.md                                          # under 500
grep -rn 'TEMPLATE:' .                                  # prints nothing
grep -nE '[$][0-9]|[$]ARGUMENTS|[$][{]CLAUDE_|!`' SKILL.md   # prints nothing
```
