#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
PORT="${PORT:-8504}"
exec "$PYTHON" -m streamlit run app.py --server.port "$PORT" --server.address "${HOST:-0.0.0.0}" --server.headless true
