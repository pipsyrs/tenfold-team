# tenfold

A multi-agent development team for Claude Code. Install it, open `claude`, and type what you want built — the **Chairman** breaks it down, delegates to specialist agents, runs QA and a security scan, then reports back.

```
you ──► chairman ──► product-manager ──► architect ──► database ──► backend / designer ──► tech-lead ──► qa ──► security ──► (devops) ──► report
```

## Team

Each agent does **one job** and hands anything outside it to the right agent (`[NEEDS → agent]`), so work stays focused and token use stays low.

| Agent | Single job |
|---|---|
| `chairman` | Orchestrator and primary agent. The only one that talks to you. Routes work and reports. Never codes. |
| `product-manager` | User stories, acceptance criteria and scope. No technical decisions. |
| `architect` | Technical plan, API/data/UI contracts and task split per agent. No code. |
| `designer` | UI/UX plus the view, component and styling code. |
| `backend` | Business logic, API for web and mobile, services, authorization. |
| `database` | Schema, migrations, indexes, seeders, queries. |
| `tech-lead` | Reviews the diff for quality, conventions and consistency between agents. Reports, does not fix. |
| `qa` | Writes and runs tests against the acceptance criteria. Reports bugs, does not fix them. |
| `security` | Security scan of changed code. Always runs after QA. |
| `devops` | Build, deploy, CI/CD, containers, environment. Only called when needed. |

The Chairman only runs the agents a task needs: a small bug fix skips `product-manager` and `architect`, a task without UI skips `designer`, and so on.

### Token saving

- Every agent reads only the files in its brief or found by targeted grep/glob. No full-codebase scans.
- Agents pass work through files in `.tenfold/` (requirements, plans, reports) and refer to them by path instead of pasting them.
- Reports list file paths and one-line summaries instead of repeating code.
- `tech-lead` and `security` review only the diff.

Every agent detects your project's techstack (from `package.json`, `composer.json`, etc.) and follows its existing conventions.

## Compatibility

### Requirements

| Requirement | Version | Used for |
|---|---|---|
| Claude Code | 2.1.295+ (tested) | Plugins, `SubagentStart` hook, `effort` in agent frontmatter |
| `python3` | 3.8+ | `/tenfold:config`, `/tenfold:lang`, `/tenfold:new-agent`, `/tenfold:update`, update check hook |
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
/plugin marketplace add pipsyrs/tenfold-team
/plugin install tenfold@tenfold-team
```

Restart Claude Code. New sessions start as the Chairman automatically.

## Upgrading from dev-team

This plugin used to be called `dev-team` (marketplace `pipsyrs-agents`). The plugin ID changed, so auto update can't move you over. Reinstall:

```
/plugin uninstall dev-team@pipsyrs-agents
/plugin marketplace remove pipsyrs-agents
/plugin marketplace add pipsyrs/tenfold-team
/plugin install tenfold@tenfold-team
```

- `dev-team.json` is moved to `tenfold.json` automatically. Settings for `analyst`, `frontend` and `pentester` move to `architect`, `designer` and `security`.
- Generated agent files with the old `dev-team:generated` marker are regenerated or removed. Custom agents marked `dev-team:custom` keep working.
- New artifacts go to `.tenfold/`. You can delete the old `.dev-team/` folder.

## Usage

Just type your request:

```
add a login page with email + password
```

Or run it explicitly:

```
/tenfold:team add a login page with email + password
```

The Chairman reports each task as ✅ done / ⏳ pending / ❌ failed, followed by the security findings.

## Commands

| Command | Description |
|---|---|
| `/tenfold:team <request>` | Run the full team flow for one request. |
| `/tenfold:config ...` | Show config, enable/disable agents, set model, effort, skills, plugins, language, platform. |
| `/tenfold:lang [en\|id]` | Set output language (default `en`). |
| `/tenfold:new-agent <name> [role]` | Create your own agent. |
| `/tenfold:update [check\|now\|auto on\|off]` | Check for updates, update now, or toggle auto update. |

Settings are saved for the **current project** by default. Add `--global` to apply them to all projects.

### Configure agents

```
/tenfold:config show

/tenfold:config show                            # all agents: status, model, effort, skills + global settings
/tenfold:config show agents                     # agent list with enabled/disabled status

/tenfold:config disable designer,qa             # no names: pick from a list
/tenfold:config enable designer

/tenfold:config model list                      # available models
/tenfold:config model                           # pick a model, then the agents
/tenfold:config model sonnet                    # asks: all agents or pick agents
/tenfold:config model sonnet --all              # all agents
/tenfold:config model opus --agent architect      # one agent
/tenfold:config model opus --agent architect,qa   # several agents
/tenfold:config model reset --all

/tenfold:config effort list
/tenfold:config effort high --all               # low | medium | high | xhigh | max
/tenfold:config effort reset --agent qa

/tenfold:config skill add security-review --all
/tenfold:config skill remove security-review --all
/tenfold:config skill add taste --agent designer          # one agent only
/tenfold:config skill remove security-review --agent qa   # opt one agent out of a default skill

/tenfold:config plugin add <plugin@marketplace>
/tenfold:config plugin remove <plugin@marketplace>
```

- **model**: `inherit`, `sonnet`, `opus`, `haiku`, `fable`, or a full `claude-*` model ID. `model list` shows the known ones.
- **disable** blocks an agent with a permission deny rule (`Agent(tenfold:<name>)`, `Agent(<name>)`) in `.claude/settings.local.json` (or `~/.claude/settings.json` with `--global`) and tells the Chairman not to delegate to it. `chairman` can't be disabled.
- Without `--all` or `--agent`, `model`, `effort` and `skill` ask whether to apply to all agents or let you pick agents. `--all` also clears per-agent overrides for that setting.
- **skills** are preloaded into each agent. With `--agent`, add or remove for that agent only; removing a default skill opts just that agent out.
- **language** and **platform** apply to the whole team and reject `--agent`.
- **plugins** are installed for the whole session, so every agent can use them. They can't be set per agent.
- Changes take effect in a **new session**.

How it works: plugin agent files can't be edited, so when you change a setting, tenfold writes a copy of each affected agent to `.claude/agents/` (or `~/.claude/agents/` with `--global`) with the settings in its frontmatter. Those copies override the plugin defaults. When you reset a setting, the copy is removed and the agent falls back to the plugin default. Generated files are marked `<!-- tenfold:generated -->`. Don't edit them by hand, because they get overwritten.

### Language

```
/tenfold:lang id              # Bahasa Indonesia for this project
/tenfold:lang en --global     # English everywhere
```

Replies and reports follow the configured language. Code, identifiers and code comments stay in English.

### Custom agents

```
/tenfold:new-agent mobile "Flutter mobile developer"
/tenfold:new-agent backend "Go backend developer"     # replaces the default backend
/tenfold:new-agent docs "Technical writer" --user     # available in all projects
```

- A custom agent that uses a default agent's name **replaces** that default.
- Other custom agents are included by the Chairman when they're relevant to the task.
- Custom agents are marked `<!-- tenfold:custom -->` and get your `/tenfold:config` model, effort and skills too.

## Update

```
/tenfold:update               # check: installed vs latest version
/tenfold:update now           # update right away
/tenfold:update auto on       # install new versions automatically
/tenfold:update auto off      # only notify (default)
```

- At session start, tenfold checks for a new version at most once a day, in the background, so startup is not delayed.
- With auto update **off**, a notice tells you when a new version is available. With it **on**, the update installs in the background and the next session tells you to restart.
- Updates take effect after a restart. The auto update setting is global (`~/.claude/tenfold.json`). The last check is cached in `~/.claude/tenfold-update.json`.

## Config file

Settings live in `.claude/tenfold.json` (project) and `~/.claude/tenfold.json` (global). When both are set, the project file wins.

```json
{
  "language": "en",
  "platform": "claude-code",
  "defaults": { "model": "sonnet", "effort": "medium", "skills": ["security-review"] },
  "agents": { "architect": { "model": "opus", "effort": "high" } },
  "plugins": []
}
```

Run `/tenfold:config apply` after editing it by hand.

## Security: nothing goes to git

Files that tenfold creates in your project are kept out of git **automatically**, so they never end up on GitHub:

| File | Why it's created |
|---|---|
| `.claude/tenfold.json` | Your settings |
| `.claude/agents/*.md` marked `tenfold:generated` or `tenfold:custom` | Generated and custom agents |
| `.claude/settings.local.json` | Makes your configured `chairman` the primary agent |
| `.tenfold/` | Reports, notes, ADRs and scan/test results written by agents |

- They are added to your project's `.gitignore` under a `# tenfold` header. Agents also add `/.tenfold/` before writing their first artifact.
- This runs on every `/tenfold:config`, `/tenfold:lang` and `/tenfold:new-agent`.
- If one of these files was already committed, tenfold prints a warning. Untrack it with `git rm --cached <file>`.
- Global settings (`--global`) live in `~/.claude/`, outside your project.
- tenfold never stores credentials. Plugins you add with `plugin add` are installed with `claude plugin install`, so only add plugins you trust.

To share settings with your team on purpose, remove the entry from `.gitignore` or run `git add -f .claude/tenfold.json`.

## Repository layout

```
.claude-plugin/marketplace.json   marketplace manifest
platforms/claude-code/            Claude Code plugin
  .claude-plugin/plugin.json
  agents/                         agent prompts — edit agents HERE
  commands/                       slash commands
  hooks/hooks.json                language injection
  scripts/devteam.py              config + agent generation
  scripts/lang-context.sh         language hook
  scripts/spawn-team.sh           optional: VS Code tasks per agent
  settings.json                   sets chairman as the primary agent
```

### Development

```sh
# after editing platforms/claude-code/agents/*
claude plugin validate .
claude plugin validate platforms/claude-code

# test locally
claude plugin marketplace add ./
claude plugin install tenfold@tenfold-team
```

Bump `version` in both `plugin.json` and `marketplace.json` before releasing.

## Uninstall

```
/plugin uninstall tenfold@tenfold-team
```

Remove generated agent copies if you used `/tenfold:config`: delete the files marked `tenfold:generated` in `.claude/agents/` and `~/.claude/agents/`. If `.claude/settings.local.json` contains `"agent": "chairman"` or `Agent(...)` deny rules added by `disable`, remove them too (run `/tenfold:config enable <agents>` before uninstalling to do it automatically). Then remove the `# tenfold` lines from `.gitignore`, and delete `.tenfold/` and `~/.claude/tenfold-update.json`.

## Troubleshooting

- **Agents appear twice**: you have old copies in `~/.claude/agents/` without the tenfold marker. Delete them.
- **`skip ... (not generated by tenfold)`**: an agent file with the same name already exists and wasn't created by tenfold, so it's left alone. Rename or delete it.
- **Settings don't apply**: start a new session.
- **Calling `chairman` as a subagent doesn't delegate**: subagents can't spawn other subagents. Use it as the primary agent (the default) or run `/tenfold:team`.

## Author

pipsyrs — apiprs24@gmail.com
