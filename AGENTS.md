# AGENTS.md

This repo is the single source of truth for agent skills. Each skill is symlinked
into Claude Code, GitHub Copilot, and OpenAI Codex, so every skill must work in
all three unchanged.

## Layout

```
skills/<skill-name>/
  SKILL.md        # required: frontmatter + instructions
  references/     # optional: docs the agent reads on demand
  scripts/        # optional: code the agent runs
  assets/         # optional: templates/files used in output
  evals/          # test prompts: evals.json, trigger.json
templates/skill/  # copy this to start a new skill
docs/skill-authoring.md  # the full guidelines
docs/agent-support.md    # per-agent facts (folders, fields, budgets), dated
tools/            # maintenance scripts for humans; no skill uses them
```

## Before creating or editing a skill

Read `docs/skill-authoring.md`. Start new skills by copying `templates/skill/`
to `skills/<skill-name>/`.

## Non-negotiable rules

- Frontmatter has `name` and `description`. `license`, `compatibility`, and
  `metadata` are optional. Agent-specific fields are off by default (see the
  guide's "Frontmatter" section), except `disable-model-invocation` for
  manual-only skills.
- `name` matches the folder name: lowercase letters, digits, single hyphens,
  max 64 chars.
- `description` says what the skill does **and** when to use it, main use case
  first, in third person, max 1024 chars. It is the only part the agent sees
  before deciding to load the skill.
- `SKILL.md` stays under 500 lines. Move detail into `references/`.
- Paths are relative to the skill folder, use forward slashes, and never point
  outside it. A `SKILL.md` that runs commands says "Paths below are relative to
  this skill's folder."
- No agent-specific syntax in `SKILL.md`. That means no tool names (Read, Bash,
  Grep…), no slash-command assumptions, no `$ARGUMENTS`, `$0`–`$9`, or
  `${CLAUDE_…}` placeholders, and no `` !`command` `` or ```` ```! ```` blocks.
  Claude Code rewrites or runs these even inside code blocks, so shell code that
  needs them goes in `scripts/`.
- Scripts use POSIX `sh` or `python3` standard library, are executable, and
  resolve paths from their own location.
- No secrets, tokens, or personal data anywhere in a skill.
- Run through the checklist at the end of the guide before calling a skill done.
