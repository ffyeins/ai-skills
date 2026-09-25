---
# TEMPLATE: rename to match the folder: lowercase, digits, hyphens, max 64 chars.
name: skill-name
# TEMPLATE: what it does + when to use it, main use case first, third person,
# TEMPLATE: max 1024 chars (aim for under ~500), no angle brackets, no steps.
# TEMPLATE: this is the only text the agent sees when deciding to load the skill.
description: Does X for Y. Use whenever the user mentions A, B, or C, even if
  they don't name X directly. Not for Z.
---

<!--
TEMPLATE: delete this comment, every other TEMPLATE note, and every section you
don't need. The whole file loads into context when the skill triggers and stays
there for the session, so every line costs. Keep it under 500 lines; move
detail into references/. Write the test prompts in evals/ before the body.
Portability: no tool names, no argument placeholders or Claude variables, no
inline shell commands, and relative paths only (see the guide's Portability
section).
-->

# Skill Title

One or two sentences: what this skill does and the core approach.
Paths below are relative to this skill's folder.

## When not to use

- Case that looks similar but belongs elsewhere, and what to do instead.

## Workflow

1. First step, written as an instruction. Say why if it isn't obvious.
2. Run `scripts/example.sh <input>` and check its output.
3. If the check fails, fix the cause and repeat step 2.
4. Check the result: the command to run, or the file that must exist.

## Examples

**Input:** a realistic user request

**Output:**

```
the exact shape of a good result
```

## Reference files

- `references/topic.md`: what it covers. Read only when the task involves the topic.
