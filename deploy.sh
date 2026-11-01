#!/usr/bin/env bash
set -Eeuo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if ! command -v docker >/dev/null 2>&1; then
    echo "Errore: Docker non è installato o non è nel PATH." >&2
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "Errore: Docker non è avviato o non è accessibile." >&2
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "Errore: è necessario Docker Compose v2 o successivo." >&2
    exit 1
fi

if [[ ! -f .env ]]; then
    echo "Errore: crea il file .env nella directory del progetto prima del deploy." >&2
    exit 1
fi

docker compose -f compose.yaml config --quiet

echo "Build e avvio dell'applicazione..."
if ! docker compose -f compose.yaml up --build --detach --wait --wait-timeout 120; then
    echo "Deploy fallito. Stato e ultimi log:" >&2
    docker compose -f compose.yaml ps --all
    docker compose -f compose.yaml logs --tail 100 api
    exit 1
fi

docker compose -f compose.yaml ps
echo "Deploy completato. Indirizzo pubblicato:"
docker compose -f compose.yaml port api 8000
