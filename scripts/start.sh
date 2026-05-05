#!/usr/bin/env bash
set -euo pipefail

alembic upgrade head
python -m app.cli.manage seed-versions
uvicorn app.main:app --host "${APP_HOST:-0.0.0.0}" --port "${APP_PORT:-8000}"
