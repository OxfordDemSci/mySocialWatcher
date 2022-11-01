#!/bin/sh

# kill launch script
python3 utils/kill.py "launch.py"

# kill all collections
for file in specs/specs*.json
do
  python3 utils/kill.py $file
  sleep 1
done

# cleanup old logs
find /app/data/logs/* -mtime +7 -exec rm {} \;
find /app/data/collecting/* -mtime +7 -exec rm {} \;
find /app/data/finished/* -mtime +7 -exec rm {} \;
find /app/data/skeleton/* -mtime +7 -exec rm {} \;
find /app/data/tmp/* -mtime +7 -exec rm {} \;
