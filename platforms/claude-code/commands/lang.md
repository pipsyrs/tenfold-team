---
description: Set dev-team output language (en/id). Default en.
argument-hint: "[en|id] [--global]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py:*)
---

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py language $ARGUMENTS`

Confirm the result above to the user in one line. If a language was just set, use that language for the rest of this session.
