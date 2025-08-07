#!/bin/bash

docker logs datahub_web --tail 10000 | grep 'POST /api/v1/write' | grep "$(date --date='-1 hour -1 minute' '+%d/%b/%Y:%H:%M:')" | wc -l
