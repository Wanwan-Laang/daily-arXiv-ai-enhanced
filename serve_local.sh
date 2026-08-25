#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

URL="http://127.0.0.1:8000/"

echo "Starting local reading website at ${URL}"
echo "Press Ctrl-C to stop the local reading website."

python -m http.server 8000 >/tmp/daily-arxiv-http-server.log 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT INT TERM

sleep 1
open "$URL"
wait "$SERVER_PID"
