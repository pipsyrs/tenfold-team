#!/bin/sh
# Inject output language from dev-team config (project overrides user, default en)
EVENT="${1:-SessionStart}"
LANG_CODE=en
for f in "$HOME/.claude/dev-team.json" "${CLAUDE_PROJECT_DIR:-.}/.claude/dev-team.json"; do
  [ -f "$f" ] || continue
  v=$(sed -n 's/.*"language"[[:space:]]*:[[:space:]]*"\([a-zA-Z]*\)".*/\1/p' "$f" | head -n 1)
  [ -n "$v" ] && LANG_CODE=$v
done
case "$LANG_CODE" in
  id) MSG="dev-team: Gunakan Bahasa Indonesia untuk semua respons dan laporan ke user. Kode, nama variabel, dan komentar kode tetap bahasa Inggris." ;;
  *)  MSG="dev-team: Use English for all responses and reports to the user." ;;
esac
printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":"%s"}}\n' "$EVENT" "$MSG"
