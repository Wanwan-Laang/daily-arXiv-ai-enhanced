#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "Open http://127.0.0.1:8000 in your browser."
echo "Press Ctrl-C to stop the local reading website."
python -m http.server 8000
