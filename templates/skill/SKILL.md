---
# Rename to match the folder: lowercase, digits, hyphens, max 64 chars.
name: skill-name
# What it does + when to use it, third person, max 1024 chars, no angle brackets.
# This is the only text the agent sees when deciding to load the skill.
# See docs/skill-authoring.md#4-description in the ai-skills repo.
description: Does X for Y. Use whenever the user mentions A, B, or C, even if
  they don't name X directly. Not for Z.
---

<!--
Template notes: delete this comment and every section you don't need.
The whole file loads into context when the skill triggers, so every line costs.
Keep it under 500 lines; move detail into references/.
Portability: no tool names, no $ARGUMENTS, no !`cmd`, relative paths only.
-->

# Skill Title

One or two sentences: what this skill does and the core approach.

## When not to use

- Case that looks similar but belongs elsewhere, and what to do instead.

## Workflow

1. First step. Say why if it isn't obvious.
2. Run `scripts/example.sh <input>` and check its output.
3. If the check fails, fix the cause and repeat step 2.

## Examples

**Input:** a realistic user request

**Output:**

```
the exact shape of a good result
```

## Reference files

- `references/topic.md`: what it covers. Read only when the task involves the topic.
