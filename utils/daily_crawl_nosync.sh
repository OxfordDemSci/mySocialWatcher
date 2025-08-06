#!/usr/bin/env bash
set -euo pipefail

# ——— USAGE & SANITY CHECK ———
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <path-to-repo>" >&2
  exit 1
fi

REPO_DIR=$1

if [[ ! -d "$REPO_DIR" ]]; then
  echo "Error: directory '$REPO_DIR' does not exist." >&2
  exit 1
fi

# ——— STEP 0: helper vars ———
DOCKER_CRAWLER_DIR="$REPO_DIR/docker/crawler"
DATA_CRAWLER_DIR="$REPO_DIR/data/crawler"

# ——— STEP 1: stop existing crawlers ———
echo ">>> Stopping any running crawler containers…"
pushd "$DOCKER_CRAWLER_DIR" >/dev/null
docker compose stop

# ——— STEP 2: cleanup temp files ———
echo ">>> Removing temporary crawler files (*.temp.txt)…"
find "$DATA_CRAWLER_DIR" -type f -name '*temp.txt' \
  -print \
  -exec rm -f {} +

# ——— STEP 3: launch replicated crawlers ———
echo ">>> Starting crawler replicas…"
docker compose -f docker-compose-withreplicas.yml up -d
popd >/dev/null

echo ">>> All steps completed successfully."
