#!/bin/bash

VM="saffron"
COLLECTIONS=("ukraine_europe_homerecent" "ukraine_language_homerecent" "ukraine_neighbours_homerecent" "ukraine_regions_homerecent")
DIR="/home/ubuntu/mySocialWatcher"

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
docker compose up --build --no-start

unset VM
unset COLLECTIONS
unset DIR
