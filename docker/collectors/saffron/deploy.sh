#!/bin/bash

VM="saffron"
COLLECTIONS=("ukraine_countries" "ukraine_europe" "ukraine_language" "ukraine_neighbours1" "ukraine_neighbours2" "ukraine_regions")
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
docker-compose up -d --build

unset VM
unset COLLECTIONS
unset DIR
