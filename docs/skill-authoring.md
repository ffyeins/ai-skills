# Skill authoring guide

How to write skills in this repo so they trigger reliably, stay small, and work
the same in Claude Code, GitHub Copilot, and OpenAI Codex.

## Contents

1. [How skills load](#1-how-skills-load)
2. [Portability](#2-portability)
3. [Naming](#3-naming)
4. [Description](#4-description)
5. [Body](#5-body)
6. [Bundled files](#6-bundled-files)
7. [Testing](#7-testing)
8. [Security and hygiene](#8-security-and-hygiene)
9. [Installing](#9-installing)
10. [Checklist](#10-checklist)

---

## 1. How skills load

Every agent loads a skill in three stages:

| Stage | What loads | When | Cost |
|---|---|---|---|
| 1. Metadata | `name` + `description` | Always, for every installed skill | ~100 tokens per skill, all the time |
| 2. Body | The rest of `SKILL.md` | When the agent decides the skill is relevant | Up to a few thousand tokens |
| 3. Resources | Files in `references/`, `scripts/`, `assets/` | Only when the body tells the agent to open or run them | Only what's used |

Two consequences shape everything below:

- **The description is the trigger.** The agent chooses skills from stage 1
  alone. A vague description means the skill never loads, however good the body.
- **The body competes for context.** Once loaded, every line sits next to the
  user's conversation and code. Put only what's needed every time in the body,
  and move the rest into files the agent opens on demand.

## 2. Portability

The shared format covers everything a skill needs. Each agent adds its own
extras on top, and other agents either ignore them or show them as plain text.
**Write only to the shared format, unless an extra is harmless when ignored.**

### Where each agent looks

| Agent | Personal skills folder | Repo rules file |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `CLAUDE.md` |
| OpenAI Codex | `~/.agents/skills/` | `AGENTS.md` |
| GitHub Copilot | `~/.copilot/skills/`, `~/.agents/skills/`, `~/.claude/skills/` | `AGENTS.md` |

This repo keeps `AGENTS.md` as the source and `CLAUDE.md` as a symlink to it.

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
- `compatibility`: requirements outside the skill, e.g.
  `Requires python3 and network access`. Omit if there are none.
- `metadata`: free-form key/value pairs, e.g. `version: "1.0"`.

Agent-specific fields are **off by default**:

| Field | Agent | Why it's off |
|---|---|---|
| `allowed-tools` | Claude (experimental in the shared format) | Tool names differ per agent |
| `disable-model-invocation`, `user-invocable` | Claude, some Copilot clients | Others ignore them, so the skill may still start on its own |
| `argument-hint` | Claude, Copilot | Only affects slash-command UI |
| `model`, `context`, `agent`, `hooks` | Claude | No equivalent elsewhere |
| `agents/openai.yaml` (a file, not a field) | Codex | Codex UI metadata only |

Use one only when you can say why in a YAML comment next to it, and when the
skill still behaves correctly in an agent that ignores it.

**Never rely on `disable-model-invocation` to stop a skill from running.**
Codex ignores it and may start the skill on its own. If a skill does something
that shouldn't happen unprompted (deploys, deletes, sends messages), say so in
the description ("Only when the user explicitly asks to…") and make the first
step of the body confirm with the user.

### Body

| Don't write | Why | Write instead |
|---|---|---|
| "Use the Read tool on `references/api.md`" | Tool names differ per agent | "Read `references/api.md`" |
| "Run it with the Bash tool" | Same | "Run `scripts/check.sh`" |
| `$ARGUMENTS`, `$1` | Only Claude fills these in | "The user supplies a file path; if they didn't, ask for one" |
| `` !`git status` `` | Only Claude runs it before loading; others print it | "Run `git status` first" |
| "Spawn a subagent to…" | Not every agent has subagents | Describe the work; let the agent decide how |
| "The user invoked `/skill-name`" | Skills also start automatically | Handle both ways of starting |

### Paths

- Write every path relative to the skill folder: `references/api.md`, not
  `/Users/…/ai-skills/skills/x/references/api.md`.
- Use forward slashes.
- Don't reference anything outside the skill folder, including other skills or
  this repo's `docs/`. The skill is used through a symlink, so it can't assume
  where it lives or what's next to it.

### Scripts

- Use POSIX `sh` or `python3` with only the standard library. If a script needs
  anything else, say so in `compatibility` and in the body.
- Make them executable (`chmod +x`) with a shebang line.
- Resolve files from the script's own location, not the current directory:
  - sh: `dir="$(cd "$(dirname "$0")" && pwd)"`
  - python: `Path(__file__).resolve().parent`
- Assume they may run on macOS or Linux, so avoid GNU-only flags (`sed -i ''` vs
  `sed -i`, `date -d`, …).

## 3. Naming

- Lowercase letters, digits, and single hyphens, 1–64 chars:
  `^[a-z0-9]+(-[a-z0-9]+)*$`.
- Must match the folder name exactly.
- Don't use `claude` or `anthropic`, which some agents reserve.
- Be specific: `openwrt-firewall`, `pdf-form-filling`. Avoid `helper`, `utils`,
  `tools`.
- Keep it unique across everything installed on the machine, not just this
  repo. When two skills share a name, one silently shadows the other.

## 4. Description

This is the most important line in the skill, so rewrite it until it's right.

**Rules**

- 1024 characters max. Aim for 1–3 sentences.
- Third person ("Configures…", "Use when…"). It goes into the agent's system
  prompt, where "I" and "you" read wrong.
- State **what** the skill does and **when** to use it.
- Include the words users actually type: file extensions, tool names, error
  messages, common phrasings.
- Name close cases that should **not** trigger it when confusion is likely.
- No angle brackets (`<`, `>`); some agents treat the text as XML.
- Lean slightly assertive. Agents tend to skip skills more often than they
  over-use them, so "Use whenever…" beats "Can help with…".

**Examples**

Bad, which never triggers because it names nothing concrete:

```yaml
description: Helps with documents.
```

Bad, which says what but not when:

```yaml
description: A comprehensive toolkit for spreadsheet manipulation.
```

Good:

```yaml
description: Configures OpenWrt routers through UCI — firewall4/nftables zones
  and rules, DHCP and DNS with dnsmasq, VLANs on DSA switches, WireGuard. Use
  whenever the user mentions OpenWrt, LuCI, uci commands, or /etc/config files,
  even if they don't say "OpenWrt". Not for generic Linux iptables or pfSense.
```

## 5. Body

**Assume the agent is smart.** Include only what it wouldn't already know or
would likely get wrong: your conventions, your environment, non-obvious steps,
known pitfalls. For each paragraph, ask whether the skill works worse without
it. If not, delete it.

**Explain why, don't shout.** "Always sort by date, because reports are read
top-down by recency" works better than "ALWAYS sort by date!!!". Once the agent
knows the reason, it handles cases you didn't list.

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

**Write workflows as numbered steps.** For multi-step or risky tasks, add a
checklist the agent can copy and tick off, plus a validation loop:
*do → check → fix → check again*.

**Show, don't describe.** One concrete input → output example beats a paragraph
of rules, especially for formats like commit messages or report layouts.

**Stay consistent.** Pick one term per concept (e.g. always "endpoint", never a
mix of "URL", "route", and "path").

**Avoid time-sensitive facts.** No "as of 2026" or "the new API". If old
behavior matters, put it under a clearly marked "Legacy" heading.

**Suggested structure** (adapt it; don't pad sections you don't need):

```markdown
# Skill Title
One or two sentences: what this does and the core approach.

## When not to use          (only if the description can't cover it)
## Workflow                 (numbered steps)
## Examples                 (input → output)
## Reference files          (what each file holds and when to read it)
```

## 6. Bundled files

Keep `SKILL.md` under **500 lines** (roughly 5k tokens). Past that, split it.

```
skill-name/
  SKILL.md
  references/   # read on demand: API details, schemas, long guides
  scripts/      # run, don't read: deterministic or repetitive work
  assets/       # used in output: templates, boilerplate, images
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
- **Say whether to run or read each script.** "Run `scripts/validate.py
  out.json`" tells the agent to execute it, so only the output uses context.
  "See `scripts/validate.py` for the rules" tells it to read the source.
- **Turn repeated work into a script.** If testing shows the agent writing
  the same helper code every time, bundle it as a script.
- **Make scripts fail helpfully.** Print what went wrong and how to fix it,
  rather than a bare traceback. Explain constants
  (`TIMEOUT = 30  # slow networks`) instead of leaving magic numbers.

## 7. Testing

A skill isn't done until you've watched an agent use it.

1. **Write 3+ test prompts first**, before writing the skill. Make them
   realistic, the way you'd actually type them: casual phrasing, real file
   names, some context. Skip clean textbook requests.
2. **Test triggering.** Write a few prompts that should trigger the skill and
   a few near-misses that shouldn't. Start fresh sessions and see whether the
   skill loads. If it's wrong, fix the description, not the body.
3. **Test the result.** Run each prompt and check the output. Compare against
   running without the skill; if there's no difference, the skill isn't adding
   anything.
4. **Watch what the agent reads.** Files it never opens may be unnecessary or
   badly signposted. Files it opens every time may belong in `SKILL.md`.
5. **Test in every target agent.** At minimum, run one prompt each in Claude
   Code, Copilot, and Codex.
6. **Iterate.** Fix the general cause, not the one test case. Adding a rule
   for each failure leads to overfitting.

For formal evals, benchmarks, and description tuning, use the `skill-creator`
skill.

## 8. Security and hygiene

- No secrets, tokens, hostnames, or personal data in any file. Tell the agent
  to read them from environment variables or ask the user.
- Read every script you didn't write before adding it. Skills run with the
  agent's permissions.
- If a skill makes network calls or changes things outside the working
  directory, say so in the body.
- A skill must do what its description says, with no hidden behavior.

## 9. Installing

Link each skill folder into the two personal skills folders. Together they
cover all three agents: Claude Code reads `~/.claude/skills`, Codex reads
`~/.agents/skills`, and Copilot reads both.

```sh
mkdir -p ~/.claude/skills ~/.agents/skills
ln -s ~/ai-skills/skills/<skill-name> ~/.claude/skills/<skill-name>
ln -s ~/ai-skills/skills/<skill-name> ~/.agents/skills/<skill-name>
```

To remove a skill, delete the two symlinks with `rm`, not `rm -r`.

Restart the agent or open a new session after linking. Skill lists are usually
read at startup.

> **Unverified:** because Copilot reads both folders, it may list each skill
> twice. If it does, record the behavior here.

## 10. Checklist

Before calling a skill done:

- [ ] `name` matches the folder and `^[a-z0-9]+(-[a-z0-9]+)*$`, ≤64 chars
- [ ] `description` says what + when, third person, ≤1024 chars, no `<` `>`
- [ ] No agent-specific frontmatter, or each field has a reason comment and is
      harmless if ignored
- [ ] Skills that must not start on their own say so in the description and
      confirm first
- [ ] Body has no tool names, `$ARGUMENTS`, `` !`cmd` ``, or slash-command
      assumptions
- [ ] `SKILL.md` < 500 lines, and every paragraph earns its place
- [ ] Reference files are linked one level deep (or through one routing
      index), each with "read when…"
- [ ] Reference files over 100 lines have a table of contents
- [ ] All paths are relative, use forward slashes, and stay inside the folder
- [ ] Scripts are executable, POSIX `sh` or stdlib `python3`, and resolve their
      own dir
- [ ] No secrets or personal data
- [ ] Tested: should-trigger and should-not-trigger prompts, plus one real run
      in each of Claude Code, Copilot, and Codex
