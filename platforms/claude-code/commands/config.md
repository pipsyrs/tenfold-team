---
description: Configure dev-team (model, effort, skills, plugins, language, platform) for all agents or one agent
argument-hint: "show | model <m> | effort <e> | skill add|remove <s> | plugin add|remove <p> | language en|id | platform claude-code [--agent NAME] [--global]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py:*)
---

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py $ARGUMENTS`

Summarize the result above to the user in 1-3 lines. If agent files changed, remind them to start a new session.
