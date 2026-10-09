#!/bin/sh
# Build platform packages from core/
set -e
ROOT=$(cd "$(dirname "$0")" && pwd)

# claude-code
rm -rf "$ROOT/platforms/claude-code/agents"
cp -r "$ROOT/core/agents" "$ROOT/platforms/claude-code/agents"
echo "Built: platforms/claude-code"
