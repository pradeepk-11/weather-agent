#!/bin/bash
set -e

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "⚠️  No .env file found. Copy .env.example to .env and fill in your keys."
  exit 1
fi

echo "▶ Starting MCP server on http://localhost:8000 ..."
MCP_SERVER_URL="http://localhost:8000/mcp"
uvicorn mcp_server.server:mcp.app --host 0.0.0.0 --port 8000 --reload &
MCP_PID=$!

sleep 2
echo "▶ Starting Agent web app on http://localhost:8080 ..."
MCP_SERVER_URL=${MCP_SERVER_URL} uvicorn main:app --host 0.0.0.0 --port 8080 --reload &
AGENT_PID=$!

echo ""
echo "════════════════════════════════════════"
echo "✅ Running locally"
echo "🌤  Open: http://localhost:8080"
echo "🔧  MCP:  http://localhost:8000/mcp"
echo "Press Ctrl+C to stop both services"
echo "════════════════════════════════════════"

trap "kill $MCP_PID $AGENT_PID 2>/dev/null" EXIT
wait
