#!/bin/bash
set -e

cd "$(dirname "$0")"

if [[ ! -f .env ]]; then
	echo "Missing .env file. Copy .env.example to .env and configure Google OAuth credentials."
	exit 1
fi

set -a
source .env
set +a

if [[ -z "${FLUTU_GOOGLE_CLIENT_ID:-}" || -z "${FLUTU_GOOGLE_CLIENT_SECRET:-}" ]]; then
	echo "Set FLUTU_GOOGLE_CLIENT_ID and FLUTU_GOOGLE_CLIENT_SECRET in .env."
	exit 1
fi

if [[ -z "${FLASK_SECRET_KEY:-}" ]]; then
	echo "Warning: FLASK_SECRET_KEY is unset; using the development-only fallback. Set a unique secret before deployment."
fi

if [[ -x .venv/bin/python ]]; then
	exec .venv/bin/python run.py
fi

exec python3 run.py
