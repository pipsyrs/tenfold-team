# dev-team

A multi-agent development team for Claude Code. Install it, open `claude`, and type what you want built — the **Chairman** breaks it down, delegates to specialist agents, runs QA and a security scan, then reports back.

```
you ──► chairman ──► analyst ──► frontend / backend / database ──► qa ──► pentester ──► report
```

## Team

| Agent | Role |
|---|---|
| `chairman` | Orchestrator and primary agent. The only one that talks to you. |
| `analyst` | Architecture and technical decisions before coding. |
| `frontend` | UI, components, styling. |
| `backend` | Business logic, API, services. |
| `database` | Schema, migrations, indexes, queries. |
| `qa` | Tests and code review. Reports bugs, does not fix them. |
| `pentester` | Security scan. Always runs last. |

Every agent detects your project's techstack (from `package.json`, `composer.json`, etc.) and follows its existing conventions.

## Compatibility

### Requirements

| Requirement | Version | Used for |
|---|---|---|
| Claude Code | 2.1.295+ (tested) | Plugins, `SubagentStart` hook, `effort` in agent frontmatter |
| `python3` | 3.8+ | `/dev-team:config`, `/dev-team:lang`, `/dev-team:new-agent`, `/dev-team:update`, update check hook |
| `sh` | any POSIX shell | Language hook |

Older Claude Code versions may still install the plugin, but some features (such as per-agent `effort`) may be ignored.

### AI platforms

| Platform | Status |
|---|---|
| Claude Code | ✅ Supported |
| Codex, others | 🔜 Planned |

### Where Claude Code runs

| Surface | Status |
|---|---|
| Terminal (CLI) | ✅ Tested |
| VS Code / Cursor (Claude Code extension) | ⚠️ Should work (same CLI), not tested |
| JetBrains IDEs (Claude Code plugin) | ⚠️ Should work (same CLI), not tested |
| Claude desktop app, claude.ai/code (web) | ❓ Not tested |

### Operating systems

| OS | Status |
|---|---|
| Linux | ✅ Tested |
| macOS | ⚠️ Should work, not tested |
| Windows (WSL) | ⚠️ Should work, not tested |
| Windows (native) | ❓ Not tested — needs Git Bash for hooks and `python3` on `PATH` |

### Models and effort

- **Models**: `inherit`, `sonnet`, `opus`, `haiku`, `fable`, or any full `claude-*` model ID
- **Effort**: `low`, `medium`, `high`, `xhigh`, `max`
- **Languages**: English (`en`, default), Bahasa Indonesia (`id`)

### Techstacks

Agents detect the stack from your project files and follow its conventions. They work with any stack. These have explicit guidance in the agent prompts:

| Area | Stacks |
|---|---|
| Frontend | React, Vue, Svelte, Blade, Jinja, ERB |
| Backend | Laravel, Express, Django, FastAPI, Rails, Go |
| Database / ORM | PostgreSQL, MySQL, SQLite, MongoDB, Prisma, Eloquent, SQLAlchemy |
| Testing | Jest, Pytest, PHPUnit, Pest, RSpec, Go test |
| Security scan | Any stack: injection, auth/IDOR, data exposure, CSRF, vulnerable dependencies, plus stack-specific checks |

## Install

```
/plugin marketplace add pipsyrs/dev-team
/plugin install dev-team@pipsyrs-agents
```

Restart Claude Code. New sessions start as the Chairman automatically.

## Usage

Just type your request:

```
add a login page with email + password
```

Or run it explicitly:

```
/dev-team:team add a login page with email + password
```

The Chairman reports each task as ✅ done / ⏳ pending / ❌ failed, followed by the pentester's findings.

## Commands

| Command | Description |
|---|---|
| `/dev-team:team <request>` | Run the full team flow for one request. |
| `/dev-team:config ...` | Set model, effort, skills, plugins, language, platform. |
| `/dev-team:lang [en\|id]` | Set output language (default `en`). |
| `/dev-team:new-agent <name> [role]` | Create your own agent. |
| `/dev-team:update [check\|now\|auto on\|off]` | Check for updates, update now, or toggle auto update. |

Settings are saved for the **current project** by default. Add `--global` to apply them to all projects.

### Configure agents

```
/dev-team:config show

/dev-team:config model sonnet                    # all agents
/dev-team:config model opus --agent analyst      # one agent
/dev-team:config model reset

/dev-team:config effort high                     # low | medium | high | xhigh | max
/dev-team:config effort reset --agent qa

/dev-team:config skill add security-review
/dev-team:config skill remove security-review
/dev-team:config skill add taste --agent frontend          # one agent only
/dev-team:config skill remove security-review --agent qa   # opt one agent out of a default skill

/dev-team:config plugin add <plugin@marketplace>
/dev-team:config plugin remove <plugin@marketplace>
```

- **model**: `inherit`, `sonnet`, `opus`, `haiku`, `fable`, or a full `claude-*` model ID.
- **skills** are preloaded into each agent. With `--agent`, add or remove for that agent only; removing a default skill opts just that agent out.
- **language** and **platform** apply to the whole team and reject `--agent`.
- **plugins** are installed for the whole session, so every agent can use them. They can't be set per agent.
- Changes take effect in a **new session**.

How it works: plugin agent files can't be edited, so when you change a setting, dev-team writes a copy of each affected agent to `.claude/agents/` (or `~/.claude/agents/` with `--global`) with the settings in its frontmatter. Those copies override the plugin defaults. When you reset a setting, the copy is removed and the agent falls back to the plugin default. Generated files are marked `<!-- dev-team:generated -->`. Don't edit them by hand, because they get overwritten.

### Language

```
/dev-team:lang id              # Bahasa Indonesia for this project
/dev-team:lang en --global     # English everywhere
```

Replies and reports follow the configured language. Code, identifiers and code comments stay in English.

### Custom agents

```
/dev-team:new-agent mobile "Flutter mobile developer"
/dev-team:new-agent backend "Go backend developer"     # replaces the default backend
/dev-team:new-agent docs "Technical writer" --user     # available in all projects
```

- A custom agent that uses a default agent's name **replaces** that default.
- Other custom agents are included by the Chairman when they're relevant to the task.
- Custom agents are marked `<!-- dev-team:custom -->` and get your `/dev-team:config` model, effort and skills too.

## Update

```
/dev-team:update               # check: installed vs latest version
/dev-team:update now           # update right away
/dev-team:update auto on       # install new versions automatically
/dev-team:update auto off      # only notify (default)
```

- At session start, dev-team checks for a new version at most once a day, in the background, so startup is not delayed.
- With auto update **off**, a notice tells you when a new version is available. With it **on**, the update installs in the background and the next session tells you to restart.
- Updates take effect after a restart. The auto update setting is global (`~/.claude/dev-team.json`). The last check is cached in `~/.claude/dev-team-update.json`.

## Config file

Settings live in `.claude/dev-team.json` (project) and `~/.claude/dev-team.json` (global). When both are set, the project file wins.

```json
{
  "language": "en",
  "platform": "claude-code",
  "defaults": { "model": "sonnet", "effort": "medium", "skills": ["security-review"] },
  "agents": { "analyst": { "model": "opus", "effort": "high" } },
  "plugins": []
}
```

Run `/dev-team:config apply` after editing it by hand.

## Security: nothing goes to git

Files that dev-team creates in your project are kept out of git **automatically**, so they never end up on GitHub:

| File | Why it's created |
|---|---|
| `.claude/dev-team.json` | Your settings |
| `.claude/agents/*.md` marked `dev-team:generated` or `dev-team:custom` | Generated and custom agents |
| `.claude/settings.local.json` | Makes your configured `chairman` the primary agent |
| `.dev-team/` | Reports, notes, ADRs and scan/test results written by agents |

- They are added to your project's `.gitignore` under a `# dev-team` header. Agents also add `/.dev-team/` before writing their first artifact.
- This runs on every `/dev-team:config`, `/dev-team:lang` and `/dev-team:new-agent`.
- If one of these files was already committed, dev-team prints a warning. Untrack it with `git rm --cached <file>`.
- Global settings (`--global`) live in `~/.claude/`, outside your project.
- dev-team never stores credentials. Plugins you add with `plugin add` are installed with `claude plugin install`, so only add plugins you trust.

To share settings with your team on purpose, remove the entry from `.gitignore` or run `git add -f .claude/dev-team.json`.

## Repository layout

```
.claude-plugin/marketplace.json   marketplace manifest
core/agents/                      agent prompts — edit agents HERE
platforms/claude-code/            Claude Code plugin
  .claude-plugin/plugin.json
  agents/                         built from core/ (don't edit)
  commands/                       slash commands
  hooks/hooks.json                language injection
  scripts/devteam.py              config + agent generation
  scripts/lang-context.sh         language hook
  scripts/spawn-team.sh           optional: VS Code tasks per agent
  settings.json                   sets chairman as the primary agent
build.sh                          copies core/ into each platform
```

### Development

```sh
# after editing core/agents/*
./build.sh
claude plugin validate .
claude plugin validate platforms/claude-code

# test locally
claude plugin marketplace add ./
claude plugin install dev-team@pipsyrs-agents
```

Bump `version` in both `plugin.json` and `marketplace.json` before releasing.

## Uninstall

```
/plugin uninstall dev-team@pipsyrs-agents
```

Remove generated agent copies if you used `/dev-team:config`: delete the files marked `dev-team:generated` in `.claude/agents/` and `~/.claude/agents/`. If `.claude/settings.local.json` contains `"agent": "chairman"`, remove that line too. Then remove the `# dev-team` lines from `.gitignore`, and delete `.dev-team/` and `~/.claude/dev-team-update.json`.

## Troubleshooting

- **Agents appear twice**: you have old copies in `~/.claude/agents/` without the dev-team marker. Delete them.
- **`skip ... (not generated by dev-team)`**: an agent file with the same name already exists and wasn't created by dev-team, so it's left alone. Rename or delete it.
- **Settings don't apply**: start a new session.
- **Calling `chairman` as a subagent doesn't delegate**: subagents can't spawn other subagents. Use it as the primary agent (the default) or run `/dev-team:team`.

## Author

pipsyrs — apiprs24@gmail.com
