---
description: Create a custom agent that dev-team can use alongside (or instead of) the default agents
argument-hint: "<name> [role description] [--user]"
---

Create a custom Claude Code agent from: $ARGUMENTS

Steps:
1. Parse `name` (kebab-case, lowercase) and role description. If the role is missing, ask the user ONE question for it.
2. Location: `.claude/agents/<name>.md` in the current project. If `--user` is given: `~/.claude/agents/<name>.md`.
3. If the file already exists, ask before overwriting.
4. To replace a default agent (analyst, frontend, backend, database, qa, pentester), use the same name — chairman will prefer the custom one.
5. Write the file with this structure, filled in for the role (keep it concise):

```markdown
---
name: <name>
description: <one sentence: role + when chairman should call it>
---
<!-- dev-team:custom -->

You are <role>.

## When called
Detect the project's techstack and follow existing conventions.

## Output
- File path above each code block
- Short code comments
- Need another team's help: `[NEEDS → <AGENT>]: ...`

## Rules
- <role-specific rules>
```

6. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/devteam.py" apply` so dev-team model/effort/skills settings are applied to the new agent.
7. Tell the user the file path and that it is available from the next Claude Code session.
