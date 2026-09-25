# ai-skills

Personal agent skills, written once and shared with Claude Code, GitHub Copilot,
and OpenAI Codex through symlinks.

All three agents implement the open [Agent Skills](https://agentskills.io)
format, so one skill folder works everywhere as long as it sticks to the
shared parts of that format.

- **Writing a skill:** read [docs/skill-authoring.md](docs/skill-authoring.md),
  then copy [templates/skill/](templates/skill/) to `skills/<skill-name>/`.
- **How each agent differs:** [docs/agent-support.md](docs/agent-support.md)
  covers skill folders, supported fields, and listing budgets, with sources and
  the date they were last checked.
- **Installing a skill:** see
  [Installing](docs/skill-authoring.md#10-installing) in the guide.
- **Rules for agents working in this repo:** [AGENTS.md](AGENTS.md)
  (`CLAUDE.md` is a symlink to it).
