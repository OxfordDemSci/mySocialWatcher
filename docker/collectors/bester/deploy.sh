#!/bin/bash

VM="bester"
COLLECTIONS=("dailyuk" "eupop" "migrationuk_mon_all" "migrationuk_tue_men" "migrationuk_wed_women")
DIR="~/mySocialWatcher"

# cron
sudo cp ${DIR}/docker/collectors/${VM}_crontab /etc/cron.d/

# config
cd ${DIR}
for COLLECTION in ${COLLECTIONS[@]};
do
  python3 config/collections/${COLLECTION}.py
done

# docker
cd ${DIR}/docker/collectors/${VM}
docker-compose up -d --build
