---
description: Configure dev-team (model, effort, skills, plugins, language, platform) for all agents or one agent
argument-hint: "show | model <m> | effort <e> | skill add|remove <s> | plugin add|remove <p> | language en|id | platform claude-code [--all | --agent NAME[,NAME...]] [--global]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py:*)
---

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py $ARGUMENTS`

If the output starts with `TARGET_REQUIRED`, nothing was changed yet. Ask the user with AskUserQuestion:
1. "Apply to all agents or specific agents?" with options "All agents" and "Specific agents".
2. If they pick specific agents, ask a second AskUserQuestion with `multiSelect: true` listing the agents from the `Agents:` line, split into groups of at most 4 options per question (up to 4 questions).
Then run the same command again with `--all` or `--agent name,name` added (keep any `--global`), via `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py`.

Otherwise, summarize the result above to the user in 1-3 lines. If agent files changed, remind them to start a new session.
