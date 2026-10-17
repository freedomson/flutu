#!/bin/bash
set -e

cd "$(dirname "$0")"

if [[ ! -f .env ]]; then
	echo "Ficheiro .env não encontrado. Copie .env.example para .env e configure as credenciais do Google."
	exit 1
fi

set -a
source .env
set +a

if [[ -z "${FLUTU_GOOGLE_CLIENT_ID:-}" || -z "${FLUTU_GOOGLE_CLIENT_SECRET:-}" ]]; then
	echo "Configure FLUTU_GOOGLE_CLIENT_ID e FLUTU_GOOGLE_CLIENT_SECRET no ficheiro .env."
	exit 1
fi

python3 server.py
