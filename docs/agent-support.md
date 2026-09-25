# Agent support

How each agent finds, lists, and runs skills. These details change often, so
they live here rather than in the [authoring guide](skill-authoring.md). Check
the sources before relying on a row, and update the date when you do.

**Last verified:** 2026-09-24, against the pages under [Sources](#sources).
Rows marked *observed* were tested on Claude Code 2.1.282.

## Contents

- Skill folders
- Frontmatter fields
- Starting a skill
- Listing budgets
- Claude Code body rewriting
- Duplicates, reloads, and symlinks
- Sources

## Skill folders

| Agent | Personal | Project |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/`, also in subfolders |
| OpenAI Codex | `~/.agents/skills/` | `.agents/skills/` in every folder from the working directory up to the repo root |
| GitHub Copilot (VS Code) | `~/.copilot/skills/`, `~/.claude/skills/`, `~/.agents/skills/` | `.github/skills/`, `.claude/skills/`, `.agents/skills/` |

Other sources:

- Claude Code also loads plugin skills (named `plugin:skill`), enterprise skills,
  and skills enabled on the claude.ai account.
- Codex also loads admin skills from `/etc/codex/skills` and system skills that
  ship with it.
- Copilot CLI and the Copilot cloud agent support skills too. The cloud agent
  runs on GitHub's machines, so it only sees skills committed to the repo.

## Frontmatter fields

"Not stated" means the agent's docs don't mention the field; assume it's ignored.

| Field | Shared format | Claude Code | Codex | VS Code Copilot |
|---|---|---|---|---|
| `name` | Required, max 64 chars | Optional, defaults to the folder name | Required | Required, max 64 chars |
| `description` | Required, max 1024 chars | Used (see [budgets](#listing-budgets)) | Required | Required, max 1024 chars |
| `license` | Optional | Accepted, no effect | Not stated | Not stated |
| `compatibility` | Optional, max 500 chars | Accepted, no effect | Not stated | Not stated |
| `metadata` | Optional, string map | Accepted | Not stated | Not stated |
| `allowed-tools` | Experimental | Pre-approves tools | Not stated | Not stated |
| `disable-model-invocation` | No | Yes | Not stated; use `agents/openai.yaml` | Yes |
| `user-invocable` | No | Yes (`false` hides it from the menu) | Not stated | Yes |
| `argument-hint` | No | Yes | Not stated | Yes |
| `context: fork` | No | Yes | Not stated | Experimental |
| `when_to_use` | No | Appended to `description` | Not stated | Not stated |
| `arguments`, `disallowed-tools`, `model`, `effort`, `agent`, `background`, `hooks`, `paths`, `shell` | No | Yes | Not stated | Not stated |

Codex reads a separate file, `agents/openai.yaml`, from the skill folder:

- `interface`: `display_name`, `short_description`, `icon_small`, `icon_large`,
  `brand_color`, `default_prompt`. These only affect the UI.
- `policy.allow_implicit_invocation`: default `true`. When `false`, Codex won't
  start the skill on its own, but `$skill-name` still works.
- `dependencies.tools`: MCP servers the skill needs, each with `type`, `value`,
  `description`, `transport`, and `url`.

## Starting a skill

| Agent | By name | Manual only |
|---|---|---|
| Claude Code | `/skill-name args` | `disable-model-invocation: true` |
| Codex | `$skill-name`, or pick one from `/skills` | `agents/openai.yaml`: `policy.allow_implicit_invocation: false` |
| VS Code Copilot | `/skill-name` in chat | `disable-model-invocation: true` |

Every agent can also start a skill on its own when the description matches the
request, unless the skill is marked manual-only.

## Listing budgets

| Agent | Limit |
|---|---|
| Claude Code | `description` plus `when_to_use` is cut at 1,536 characters per skill. A loaded skill stays in context for the rest of the session; after compaction, loaded skills share 25,000 tokens, most recently used first. |
| Codex | The whole skill list gets at most 2% of the context window, or 8,000 characters if the window size is unknown. Over that, Codex shortens descriptions first, then leaves skills out and shows a warning. |
| VS Code Copilot | Not stated |

## Claude Code body rewriting

Before the model sees `SKILL.md`, Claude Code rewrites parts of it. Other agents
show the same text as written.

| Written | Becomes |
|---|---|
| `$ARGUMENTS` | The arguments, or nothing if there are none (*observed*) |
| `$ARGUMENTS[N]`, `$N` (`$0`, `$1`, …) | Argument N, counting from 0. It is left as written when fewer arguments were passed (*observed*) |
| `$name` | The named argument, if `arguments` declares `name` |
| `${CLAUDE_SKILL_DIR}` | The skill's folder, as an absolute path (*observed*) |
| `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` | Their values |
| `` !`command` `` at the start of a line or after a space | The command's output. It runs when the skill loads, with no permission prompt (*observed*). It is left alone right after other characters, such as `[` |
| A code block fenced with ```` ```! ```` | The output of its commands, with the fences removed (*observed*) |

This happens everywhere in the body, including inside code blocks (*observed*:
`awk '{print $1}'` became `awk '{print beta}'`). `\$` escapes a dollar sign in
Claude Code, but other agents show the backslash, so it doesn't help a portable
skill. Files the agent reads later, such as references and scripts, are not
rewritten.

## Duplicates, reloads, and symlinks

| | Claude Code | Codex | VS Code Copilot |
|---|---|---|---|
| Same name in two places | Enterprise beats personal beats project. Plugin skills are namespaced, so they never clash | Both are listed; nothing is merged | Not stated. Linking one skill into both `~/.claude/skills` and `~/.agents/skills` may list it twice (unverified) |
| Picks up new or changed skills | Yes, without a restart (*observed*: an edit to a symlinked skill's description showed up in the same session) | Yes; restart if a change doesn't appear | Not stated |
| Symlinked skill folders | Work (*observed*: this repo's skills load through symlinks) | Followed | Not stated |
| Tells the model where the skill lives | Yes: "Base directory for this skill: …" (*observed*) | Not stated | Not stated |

## Sources

- Agent Skills specification: <https://agentskills.io/specification>
- Claude Code skills: <https://code.claude.com/docs/en/skills>
- Codex skills: <https://learn.chatgpt.com/docs/build-skills> (redirected from
  <https://developers.openai.com/codex/skills>)
- VS Code / Copilot agent skills:
  <https://code.visualstudio.com/docs/copilot/customization/agent-skills>
