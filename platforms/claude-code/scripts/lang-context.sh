#!/bin/sh
# Inject output language from tenfold config (project overrides user, default en; dev-team.json is the legacy name)
EVENT="${1:-SessionStart}"
LANG_CODE=en
P="${CLAUDE_PROJECT_DIR:-.}/.claude"
for f in "$HOME/.claude/dev-team.json" "$HOME/.claude/tenfold.json" "$P/dev-team.json" "$P/tenfold.json"; do
  [ -f "$f" ] || continue
  v=$(sed -n 's/.*"language"[[:space:]]*:[[:space:]]*"\([a-zA-Z]*\)".*/\1/p' "$f" | head -n 1)
  [ -n "$v" ] && LANG_CODE=$v
done
case "$LANG_CODE" in
  id) MSG="tenfold: Gunakan Bahasa Indonesia untuk semua respons dan laporan ke user. Kode, nama variabel, dan komentar kode tetap bahasa Inggris." ;;
  *)  MSG="tenfold: Use English for all responses and reports to the user." ;;
esac
printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":"%s"}}\n' "$EVENT" "$MSG"
