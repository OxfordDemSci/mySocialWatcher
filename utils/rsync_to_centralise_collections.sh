#!/usr/bin/env bash
set -euo pipefail

# ——— CONFIGURATION ———
# List your servers (DNS name or IP)
REMOTE_SERVERS=(
  psw_collectors
  nowpop_collectors
  dgg_collectors
  simon
)

# Path on each remote you want to sync (no trailing slash here)
REMOTE_PATH="~/mySocialWatcher/data"

# Local parent directory into which you’ll create one sub‐dir per host
LOCAL_PARENT="~/git/OxfordDemSci/mySocialWatcher/data"

# Local path to merge all crawler directories
LOCAL_CRAWLER="${LOCAL_PARENT}/crawler"

# ——— RSYNC OPTIONS ———
# -a  : archive mode (recursive, preserves perms/timestamps/etc)
# -z  : compress data in transit
# -P  : show progress and keep partially transferred files
RSYNC_BIN="$(command -v rsync)"
RSYNC_OPTS="-az --info=NAME,SKIP0"

# ——— STEP 1: per‐host sync ———
for HOST in "${REMOTE_SERVERS[@]}"; do
  echo "ls />> Syncing from ${HOST}:${REMOTE_PATH} …"
  DEST="${LOCAL_PARENT}/${HOST}"
  mkdir -p "$DEST"
  "$RSYNC_BIN" $RSYNC_OPTS \
    "${HOST}:${REMOTE_PATH}/" \
    "$DEST/"
done

# ——— STEP 2: merge all crawler/ folders ———
echo ">> Sync crawler directory from each host into ${LOCAL_CRAWLER}"
mkdir -p "$LOCAL_CRAWLER"

for HOST in "${REMOTE_SERVERS[@]}"; do
  SRC="${LOCAL_PARENT}/${HOST}/crawler/"
  if [ -d "$SRC" ]; then
    echo "   • syncing ${SRC} → ${LOCAL_CRAWLER}/${HOST}/"
    "$RSYNC_BIN" -azP \
      "$SRC" \
      "${LOCAL_CRAWLER}/${HOST}"
  else
    echo "   ⚠️  no crawler/ found for ${HOST} at ${SRC}"
  fi
done

echo ">> All syncs complete!"
