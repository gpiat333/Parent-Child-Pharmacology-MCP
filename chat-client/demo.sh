#!/bin/bash
# Ask one question of the deployed Databricks App through the companion chat client,
# which runs the safety router before any model call.
# Usage: chat-client/demo.sh "Using LactMed, summarize the evidence on sertraline during breastfeeding."
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"
export DATABRICKS_CONFIG_PROFILE="${DATABRICKS_CONFIG_PROFILE:-hackathon}"
export DATABRICKS_HOST="$(databricks auth env --profile "$DATABRICKS_CONFIG_PROFILE" 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin)['env']['DATABRICKS_HOST'])")"
export DATABRICKS_MCP_ENDPOINT="$(databricks apps get mcp-mc --profile "$DATABRICKS_CONFIG_PROFILE" -o json | python3 -c "import sys,json;print(json.load(sys.stdin)['url'].rstrip('/')+'/mcp')")"
out="$(mktemp -d)"
pwsh -NoProfile -File chat-client/test-mcp-chat.ps1 -Question "$1" -McpEndpoint "$DATABRICKS_MCP_ENDPOINT" -OutputDirectory "$out"
