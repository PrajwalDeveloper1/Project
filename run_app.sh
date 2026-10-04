#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
  echo "Virtual environment is missing. Create it first: python3 -m venv .venv"
  exit 1
fi

PORT="${PORT:-8501}"
HOST="${HOST:-0.0.0.0}"

while :; do
  if .venv/bin/python - "$PORT" <<'PY'
import socket, sys
port = int(sys.argv[1])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind(("0.0.0.0", port))
except OSError:
    raise SystemExit(1)
else:
    s.close()
    raise SystemExit(0)
PY
  then
    break
  fi
  PORT=$((PORT + 1))
  if [ "$PORT" -gt 8510 ]; then
    echo "No free port found in the 8501-8510 range."
    exit 1
  fi
done

printf 'Starting Project 3 on http://localhost:%s\n' "$PORT"
exec .venv/bin/python -m streamlit run app.py --server.port "$PORT" --server.address "$HOST" --server.headless true
