---
description: Configure dev-team (show, enable/disable agents, model, effort, skills, plugins, language, platform) for all agents or selected agents
argument-hint: "show [agents] | enable|disable <agents> | model [list|<m>] | effort [list|<e>] | skill add|remove <s> | plugin add|remove <p> | language en|id | platform claude-code [--all | --agent NAME[,NAME...]] [--global]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py:*)
---

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py $ARGUMENTS`

If the output contains `VALUE_REQUIRED`, nothing was changed yet. Ask the user with AskUserQuestion to pick a value: for model offer `opus`, `sonnet`, `haiku`, `inherit`; for effort offer `low`, `medium`, `high`, `max`. Mention in the question that the other values listed above can be typed via "Other". Then run the command again with the chosen value. It will usually answer `TARGET_REQUIRED` next.

If the output contains `AGENTS_REQUIRED`, nothing was changed yet. Ask with AskUserQuestion and `multiSelect: true` which agents to enable or disable, listing the agents from the `Agents:` line (skip `chairman` for disable), split into groups of at most 4 options per question (up to 4 questions). Then run the command again with the names as `name,name`.

If the output contains `TARGET_REQUIRED`, nothing was changed yet. Ask the user with AskUserQuestion:
1. "Apply to all agents or specific agents?" with options "All agents" and "Specific agents".
2. If they pick specific agents, ask a second AskUserQuestion with `multiSelect: true` listing the agents from the `Agents:` line, split into groups of at most 4 options per question (up to 4 questions).
Then run the same command again with `--all` or `--agent name,name` added (keep any `--global`), via `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py`.

Otherwise, summarize the result above to the user in 1-3 lines. If agent files changed, remind them to start a new session.
