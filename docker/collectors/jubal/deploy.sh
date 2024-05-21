#!/bin/bash

VM="jubal"
COLLECTIONS=("baseline_homerecent" "baseline_priority_homerecent")
DIR="/home/ubuntu/mySocialWatcher"

# cron
sudo cp ${DIR}/docker/collectors/${VM}/${VM}_crontab /etc/cron.d/

# config
cd ${DIR}
for COLLECTION in ${COLLECTIONS[@]};
do
  python3 ${DIR}/config/collections/${COLLECTION}.py
done

# docker
cd ${DIR}/docker/collectors/${VM}
docker compose up --build --no-start

unset VM
unset COLLECTIONS
unset DIR
