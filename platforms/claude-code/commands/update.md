---
description: Check for dev-team updates, update now, or toggle auto update
argument-hint: "[check|now|auto on|off]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py:*)
---

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py update $ARGUMENTS`

Summarize the result above to the user in 1-2 lines. If the plugin was updated, remind them to restart the session.
