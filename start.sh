#!/usr/bin/env bash
set -euo pipefail

: "${UVICORN_HOST:=0.0.0.0}"
: "${UVICORN_PORT:=8000}"
: "${UVICORN_WORKERS:=1}"
: "${UVICORN_RELOAD:=false}"

mkdir -p data

cmd=(uvicorn app.main:app --host "${UVICORN_HOST}" --port "${UVICORN_PORT}" --workers "${UVICORN_WORKERS}")

if [ "${UVICORN_RELOAD}" = "true" ]; then
  cmd+=(--reload)
fi

exec "${cmd[@]}"
