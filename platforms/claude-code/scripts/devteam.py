#!/usr/bin/env python3
"""dev-team config: language, platform, model, effort, skills, plugins -> generated agent files."""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parent.parent)
PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
USER_DIR = Path.home() / ".claude"
PROJECT_CLAUDE = PROJECT_DIR / ".claude"

GEN_MARK = "<!-- dev-team:generated (edit via /dev-team:config, manual edits are overwritten) -->"
CUSTOM_MARK = "<!-- dev-team:custom -->"
MAIN_AGENT = "chairman"
PLATFORMS = {"claude-code"}
LANGS = {"en", "id"}
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
MODEL_RE = re.compile(r"^(inherit|sonnet|opus|haiku|fable|claude-[a-z0-9.\-\[\]]+)$")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
SKILL_RE = re.compile(r"^[A-Za-z0-9._-]+(:[A-Za-z0-9._-]+)?$")
PLUGIN_RE = re.compile(r"^[A-Za-z0-9._-]+(@[A-Za-z0-9._-]+)?$")
KEYS = ("model", "effort", "skills")
MARKETPLACE = "pipsyrs-agents"
PLUGIN_ID = f"dev-team@{MARKETPLACE}"
UPDATE_STATE = USER_DIR / "dev-team-update.json"
UPDATE_INTERVAL = 24 * 3600


def fail(msg):
    print(f"Error: {msg}")
    sys.exit(1)


def check_add_remove(cmd, rest, regex, sep, what, example, url_hint):
    # Explain exactly which part of `<cmd> add|remove <value>` is wrong
    usage = f"usage: {cmd} add|remove <{what}>  (e.g. {cmd} add {example})"
    if not rest:
        fail(f"missing action and {what}\n{usage}")
    if rest[0] not in ("add", "remove"):
        fail(f"unknown action '{rest[0]}', use add or remove\n{usage}")
    if len(rest) < 2:
        fail(f"missing {what} after '{rest[0]}'\n{usage}")
    if len(rest) > 2:
        fail(f"expected one {what}, got {len(rest) - 1}: {' '.join(rest[1:])}\n{usage}")
    val = rest[1]
    if "://" in val or val.startswith("git@"):
        fail(f"'{val}' is a URL; {cmd} {rest[0]} takes the {what} only. {url_hint}\n{usage}")
    if not regex.match(val):
        bad = sorted({c for c in val if not re.match(r"[A-Za-z0-9._-]", c) and c != sep})
        hint = (f"invalid character(s): {' '.join(repr(c) for c in bad)}" if bad
                else f"use at most one '{sep}', not at the start or end")
        fail(f"'{val}' is not a valid {what} ({hint})\n{usage}")


def load(path):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        fail(f"{path} is not valid JSON ({e})")


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def cfg_path(base):
    return base / "dev-team.json"


def default_agents():
    return sorted(p.stem for p in (PLUGIN_ROOT / "agents").glob("*.md"))


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def strip_keys(fm):
    # Drop model/effort/skills lines (incl. YAML list items under skills)
    out, skip = [], False
    for line in fm.splitlines():
        key = line.split(":", 1)[0].strip()
        if not line.startswith((" ", "\t", "-")) and key in KEYS:
            skip = True
            continue
        if skip and line.startswith((" ", "\t", "-")):
            continue
        skip = False
        out.append(line)
    return out


def render_keys(eff):
    lines = []
    if eff.get("model"):
        lines.append(f"model: {eff['model']}")
    if eff.get("effort"):
        lines.append(f"effort: {eff['effort']}")
    if eff.get("skills"):
        lines.append("skills:")
        lines += [f"  - {s}" for s in eff["skills"]]
    return lines


def effective(cfg, name):
    eff = {k: v for k, v in cfg.get("defaults", {}).items() if v}
    agent = cfg.get("agents", {}).get(name, {})
    for k, v in agent.items():
        if k == "skills":
            eff["skills"] = sorted(set(eff.get("skills", [])) | set(v))
        elif k != "skills_removed" and v:
            eff[k] = v
    # Per-agent opt-out from default skills
    if agent.get("skills_removed"):
        eff["skills"] = sorted(set(eff.get("skills", [])) - set(agent["skills_removed"]))
    return eff


def merged_cfg(scope_base):
    user = load(cfg_path(USER_DIR))
    if scope_base == USER_DIR:
        return user
    proj = load(cfg_path(PROJECT_CLAUDE))
    out = {"defaults": dict(user.get("defaults", {})), "agents": {}}
    for k, v in proj.get("defaults", {}).items():
        if k == "skills":
            out["defaults"]["skills"] = sorted(set(out["defaults"].get("skills", [])) | set(v))
        elif v:
            out["defaults"][k] = v
    for src in (user, proj):
        for name, s in src.get("agents", {}).items():
            out["agents"].setdefault(name, {}).update(s)
    return out


def set_main_agent(base, enable):
    # Project scope uses settings.local.json so nothing lands in the repo
    path = base / ("settings.json" if base == USER_DIR else "settings.local.json")
    data = load(path)
    if enable and data.get("agent") != MAIN_AGENT:
        data["agent"] = MAIN_AGENT
        save(path, data)
    elif not enable and data.get("agent") == MAIN_AGENT:
        del data["agent"]
        save(path, data)


def apply_scope(base):
    cfg = merged_cfg(base)
    agents_dir = base / "agents"
    msgs = []
    main_generated = False
    for name in default_agents():
        target = agents_dir / f"{name}.md"
        eff = effective(cfg, name)
        exists = target.exists()
        if exists and GEN_MARK not in target.read_text():
            if eff:
                msgs.append(f"skip {target} (not generated by dev-team)")
            continue
        if not eff:
            if exists:
                target.unlink()
                msgs.append(f"removed {target} (back to plugin default)")
            continue
        fm, body = split_frontmatter((PLUGIN_ROOT / "agents" / f"{name}.md").read_text())
        lines = strip_keys(fm) + render_keys(eff)
        new = "---\n" + "\n".join(lines) + "\n---\n" + GEN_MARK + "\n" + body
        if name == MAIN_AGENT:
            main_generated = True
        if exists and target.read_text() == new:
            continue
        agents_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(new)
        msgs.append(f"wrote {target}")
    # Custom agents created by /dev-team:new-agent
    if agents_dir.is_dir():
        for p in sorted(agents_dir.glob("*.md")):
            text = p.read_text()
            if CUSTOM_MARK not in text:
                continue
            fm, body = split_frontmatter(text)
            lines = strip_keys(fm) + render_keys(effective(cfg, p.stem))
            new = "---\n" + "\n".join(lines) + "\n---\n" + body
            if new != text:
                p.write_text(new)
                msgs.append(f"updated {p}")
    set_main_agent(base, main_generated)
    return msgs


def apply_all():
    msgs = apply_scope(USER_DIR)
    if cfg_path(PROJECT_CLAUDE).exists() or (PROJECT_CLAUDE / "agents").is_dir():
        msgs += apply_scope(PROJECT_CLAUDE)
    print("\n".join(msgs) if msgs else "Agents unchanged.")
    if msgs:
        print("Changes take effect in a new Claude Code session.")
    protect_project()


IGNORE_HEADER = "# dev-team"
ARTIFACT_DIR = ".dev-team"


def git(*args):
    try:
        r = subprocess.run(["git", "-C", str(PROJECT_DIR), *args], capture_output=True, text=True, timeout=10)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def protect_project():
    # Keep dev-team files and artifacts out of git via the project .gitignore
    top = git("rev-parse", "--show-toplevel")
    if not top:
        return
    top = Path(top)
    gitignore = top / ".gitignore"
    files = [cfg_path(PROJECT_CLAUDE), PROJECT_CLAUDE / "settings.local.json"]
    agents_dir = PROJECT_CLAUDE / "agents"
    if agents_dir.is_dir():
        files += [p for p in agents_dir.glob("*.md") if GEN_MARK in p.read_text() or CUSTOM_MARK in p.read_text()]
    entries = [f"/{ARTIFACT_DIR}/"]
    for f in files:
        if not f.exists():
            continue
        try:
            entries.append("/" + f.resolve().relative_to(top.resolve()).as_posix())
        except ValueError:
            continue
    current = gitignore.read_text().splitlines() if gitignore.exists() else []
    new = [e for e in entries if e not in current]
    if not new:
        return
    if IGNORE_HEADER not in current:
        new.insert(0, IGNORE_HEADER)
    with gitignore.open("a") as fh:
        if current and current[-1] != "":
            fh.write("\n")
        fh.write("\n".join(new) + "\n")
    tracked = [e for e in entries if git("ls-files", "--error-unmatch", e.lstrip("/"))]
    print(f"git: {len(new) - (IGNORE_HEADER in new)} dev-team entr(ies) added to .gitignore")
    if tracked:
        print("Warning: already tracked by git, run `git rm --cached` on: " + ", ".join(tracked))


def check_agent(name):
    if name is None:
        return
    if not NAME_RE.match(name):
        fail(f"invalid agent name '{name}'")
    custom = any((d / "agents" / f"{name}.md").exists() for d in (USER_DIR, PROJECT_CLAUDE))
    if name not in default_agents() and not custom:
        fail(f"unknown agent '{name}'. Defaults: {', '.join(default_agents())}")


def target_section(cfg, agent):
    if agent:
        return cfg.setdefault("agents", {}).setdefault(agent, {})
    return cfg.setdefault("defaults", {})


def run_claude_plugin(action, plugin_id, scope):
    try:
        r = subprocess.run(["claude", "plugin", action, plugin_id, "--scope", scope],
                           capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        fail("'claude' CLI not found in PATH")
    out = (r.stdout + r.stderr).strip().splitlines()
    print(out[-1] if out else f"claude plugin {action} exited with {r.returncode}")
    return r.returncode == 0


def show():
    for label, base in (("user", USER_DIR), ("project", PROJECT_CLAUDE)):
        path = cfg_path(base)
        print(f"[{label}] {path}")
        print(json.dumps(load(path), indent=2) if path.exists() else "  (not set)")
    print("Defaults: language=en, platform=claude-code, model/effort=inherit, no extra skills")


def read_json(path):
    # Like load(), but never exits: used by hooks and background jobs
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}


def version_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or "0"))


def installed_version():
    return read_json(PLUGIN_ROOT / ".claude-plugin" / "plugin.json").get("version", "0")


def run_claude(*args, timeout=120):
    try:
        return subprocess.run(["claude", *args], capture_output=True, text=True, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def latest_version():
    # Refresh the marketplace clone, then read the version it publishes
    r = run_claude("plugin", "marketplace", "update", MARKETPLACE)
    if not r or r.returncode:
        return None
    known = read_json(USER_DIR / "plugins" / "known_marketplaces.json").get(MARKETPLACE, {})
    loc = Path(known.get("installLocation") or USER_DIR / "plugins" / "marketplaces" / MARKETPLACE)
    plugins = read_json(loc / ".claude-plugin" / "marketplace.json").get("plugins", [])
    return next((p.get("version") for p in plugins if p.get("name") == "dev-team"), None)


def install_scope():
    recs = read_json(USER_DIR / "plugins" / "installed_plugins.json").get("plugins", {}).get(PLUGIN_ID, [])
    return recs[0].get("scope", "user") if recs else "user"


def auto_update_on():
    return read_json(cfg_path(USER_DIR)).get("auto_update") is True


def save_state(**kw):
    state = read_json(UPDATE_STATE)
    state.update(kw)
    try:
        save(UPDATE_STATE, state)
    except OSError:
        pass


def install_update():
    r = run_claude("plugin", "update", PLUGIN_ID, "--scope", install_scope(), timeout=300)
    out = ((r.stdout + r.stderr).strip().splitlines() if r else []) or ["'claude' CLI not found or timed out"]
    return bool(r) and r.returncode == 0, out[-1]


def update_hook():
    # SessionStart: notify from cached state (no network), refresh in background when stale
    state, cur = read_json(UPDATE_STATE), installed_version()
    latest = state.get("latest")
    if latest and version_tuple(latest) > version_tuple(cur):
        if state.get("updated_to") == latest:
            msg = f"dev-team updated to {latest}. Restart the session to apply."
        else:
            msg = f"dev-team {latest} is available (installed {cur}). Run /dev-team:update now"
        print(json.dumps({"systemMessage": msg}))
    if time.time() - state.get("checked", 0) >= UPDATE_INTERVAL:
        save_state(checked=time.time())
        subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "update", "background"],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)


def update_background():
    latest = latest_version()
    if not latest:
        return
    save_state(latest=latest)
    if auto_update_on() and version_tuple(latest) > version_tuple(installed_version()):
        ok, _ = install_update()
        if ok:
            save_state(updated_to=latest)


def update(rest):
    sub = rest[0] if rest else "check"
    if sub == "hook":
        return update_hook()
    if sub == "background":
        return update_background()
    if sub == "auto":
        if len(rest) != 2 or rest[1] not in ("on", "off"):
            fail("usage: update auto on|off")
        cfg = load(cfg_path(USER_DIR))
        cfg["auto_update"] = rest[1] == "on"
        save(cfg_path(USER_DIR), cfg)
        when = "installs" if rest[1] == "on" else "only notifies about"
        print(f"auto update: {rest[1]} (dev-team checks once a day at session start and {when} new versions)")
        return
    if sub not in ("check", "now"):
        fail(f"unknown update action '{sub}'\nusage: update [check|now|auto on|off]")
    cur = installed_version()
    latest = latest_version()
    if not latest:
        fail(f"could not check for updates (`claude plugin marketplace update {MARKETPLACE}` failed)")
    save_state(checked=time.time(), latest=latest)
    auto = "on" if auto_update_on() else "off"
    if version_tuple(latest) <= version_tuple(cur):
        print(f"dev-team {cur} is up to date (auto update: {auto})")
        return
    if sub == "check":
        print(f"dev-team {latest} is available (installed {cur}, auto update: {auto}). Run /dev-team:update now")
        return
    ok, last = install_update()
    if not ok:
        fail(f"update failed: {last}")
    save_state(updated_to=latest)
    print(f"dev-team updated {cur} -> {latest}. Restart the session to apply.")


USAGE = """Usage: devteam.py <command> [args] [--agent NAME] [--global]
  show
  apply
  language en|id
  platform claude-code
  model <inherit|sonnet|opus|haiku|fable|claude-...|reset>
  effort <low|medium|high|xhigh|max|reset>
  skill add|remove <name>
  plugin add|remove <plugin[@marketplace]>
  update [check|now|auto on|off]
--global writes ~/.claude (default: current project)."""


def main(argv):
    agent, is_global, args = None, False, []
    it = iter(argv)
    for a in it:
        if a == "--agent":
            agent = next(it, None) or fail("--agent needs a name")
        elif a in ("--global", "--user"):
            is_global = True
        else:
            args.append(a)
    if not args:
        print(USAGE)
        return
    cmd, rest = args[0], args[1:]
    base = USER_DIR if is_global else PROJECT_CLAUDE
    path = cfg_path(base)
    cfg = load(path)

    if cmd == "update":
        return update(rest)
    if cmd == "show":
        return show()
    if cmd == "apply":
        return apply_all()
    if agent and cmd in ("language", "lang", "platform"):
        fail(f"{cmd} applies to the whole team (all agents); drop --agent")
    if cmd in ("language", "lang"):
        if not rest:
            print(f"language: {cfg.get('language', 'en (default)')}")
            return
        if rest[0].lower() not in LANGS:
            fail(f"language must be one of {sorted(LANGS)}")
        cfg["language"] = rest[0].lower()
        save(path, cfg)
        print(f"language = {cfg['language']} ({path})")
        return protect_project()
    if cmd == "platform":
        if not rest or rest[0] not in PLATFORMS:
            fail(f"supported platforms: {sorted(PLATFORMS)} (codex etc. coming later)")
        cfg["platform"] = rest[0]
        save(path, cfg)
        print(f"platform = {rest[0]}")
        return protect_project()

    check_agent(agent)
    sec = target_section(cfg, agent)
    who = agent or "all agents"

    if cmd in ("model", "effort"):
        if not rest:
            fail(f"{cmd} needs a value")
        val = rest[0].lower() if cmd == "effort" else rest[0]
        if val == "reset":
            sec.pop(cmd, None)
        elif cmd == "model" and not MODEL_RE.match(val):
            fail("model must be inherit|sonnet|opus|haiku|fable or a claude-* model id")
        elif cmd == "effort" and val not in EFFORTS:
            fail(f"effort must be one of {sorted(EFFORTS)}")
        else:
            sec[cmd] = val
        save(path, cfg)
        print(f"{cmd} = {sec.get(cmd, 'reset')} for {who}")
        return apply_all()

    if cmd == "skill":
        check_add_remove("skill", rest, SKILL_RE, ":", "skill name", "my-skill or plugin:skill",
                         "Install the skill into .claude/skills/ or ~/.claude/skills/ first, then add it by its name")
        action, name = rest
        skills = set(sec.get("skills", []))
        if agent:
            current = set(effective(merged_cfg(base), agent).get("skills", []))
            removed = set(sec.get("skills_removed", []))
        else:
            current, removed = skills, set()
        if action == "add":
            if name in current:
                fail(f"skill '{name}' is already set for {who}")
            skills.add(name)
            removed.discard(name)
        else:
            if name not in current:
                fail(f"skill '{name}' is not set for {who}. Current: {', '.join(sorted(current)) or 'none'}")
            skills.discard(name)
            if agent:
                removed.add(name)  # also opts out if it comes from the defaults
        sec["skills"] = sorted(skills)
        if removed:
            sec["skills_removed"] = sorted(removed)
        else:
            sec.pop("skills_removed", None)
        save(path, cfg)
        shown = effective(merged_cfg(base), agent).get("skills", []) if agent else sec["skills"]
        print(f"skills for {who}: {shown or 'none'}")
        return apply_all()

    if cmd == "plugin":
        if agent:
            fail("plugins apply to the whole session (all agents); drop --agent")
        check_add_remove("plugin", rest, PLUGIN_RE, "@", "plugin[@marketplace]", "dev-team@pipsyrs-agents",
                         "Add the marketplace first with `/plugin marketplace add <url>`, then add the plugin by name")
        action = "install" if rest[0] == "add" else "uninstall"
        if not run_claude_plugin(action, rest[1], "user" if is_global else "project"):
            sys.exit(1)
        plugins = set(cfg.get("plugins", []))
        (plugins.add if rest[0] == "add" else plugins.discard)(rest[1])
        cfg["plugins"] = sorted(plugins)
        save(path, cfg)
        print(f"plugins: {cfg['plugins'] or 'none'} (available to every agent)")
        return protect_project()

    fail(f"unknown command '{cmd}'\n{USAGE}")


if __name__ == "__main__":
    main(sys.argv[1:])
