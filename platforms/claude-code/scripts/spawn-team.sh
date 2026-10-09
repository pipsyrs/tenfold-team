#!/bin/bash
mkdir -p .vscode

cat > .vscode/tasks.json << 'TASKS'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "👑 chairman",
      "type": "shell",
      "command": "claude --agent dev-team:chairman",
      "presentation": { "panel": "dedicated", "reveal": "always", "focus": true }
    },
    {
      "label": "🔍 analyst",
      "type": "shell",
      "command": "claude --agent dev-team:analyst",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "🎨 frontend",
      "type": "shell",
      "command": "claude --agent dev-team:frontend",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "⚙️ backend",
      "type": "shell",
      "command": "claude --agent dev-team:backend",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "🗄️ database",
      "type": "shell",
      "command": "claude --agent dev-team:database",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "✅ qa",
      "type": "shell",
      "command": "claude --agent dev-team:qa",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "🔐 pentester",
      "type": "shell",
      "command": "claude --agent dev-team:pentester",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "🚀 Spawn Dev Team",
      "dependsOrder": "parallel",
      "dependsOn": [
        "👑 chairman",
        "🔍 analyst",
        "🎨 frontend",
        "⚙️ backend",
        "🗄️ database",
        "✅ qa",
        "🔐 pentester"
      ],
      "group": { "kind": "build", "isDefault": true }
    }
  ]
}
TASKS

echo "✅ tasks.json siap — Ctrl+Shift+B untuk spawn semua agent"
