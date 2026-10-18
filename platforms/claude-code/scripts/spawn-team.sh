#!/bin/bash
mkdir -p .vscode

cat > .vscode/tasks.json << 'TASKS'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "👑 chairman",
      "type": "shell",
      "command": "claude --agent tenfold:chairman",
      "presentation": { "panel": "dedicated", "reveal": "always", "focus": true }
    },
    {
      "label": "📋 product-manager",
      "type": "shell",
      "command": "claude --agent tenfold:product-manager",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "🏗️ architect",
      "type": "shell",
      "command": "claude --agent tenfold:architect",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "🎨 designer",
      "type": "shell",
      "command": "claude --agent tenfold:designer",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "⚙️ backend",
      "type": "shell",
      "command": "claude --agent tenfold:backend",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "🗄️ database",
      "type": "shell",
      "command": "claude --agent tenfold:database",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "🧭 tech-lead",
      "type": "shell",
      "command": "claude --agent tenfold:tech-lead",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "✅ qa",
      "type": "shell",
      "command": "claude --agent tenfold:qa",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "🔐 security",
      "type": "shell",
      "command": "claude --agent tenfold:security",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "🚀 devops",
      "type": "shell",
      "command": "claude --agent tenfold:devops",
      "presentation": { "panel": "dedicated", "reveal": "silent", "focus": false }
    },
    {
      "label": "🚀 Spawn Tenfold Team",
      "dependsOrder": "parallel",
      "dependsOn": [
        "👑 chairman",
        "📋 product-manager",
        "🏗️ architect",
        "🎨 designer",
        "⚙️ backend",
        "🗄️ database",
        "🧭 tech-lead",
        "✅ qa",
        "🔐 security",
        "🚀 devops"
      ],
      "group": { "kind": "build", "isDefault": true }
    }
  ]
}
TASKS

echo "✅ tasks.json siap — Ctrl+Shift+B untuk spawn semua agent"
