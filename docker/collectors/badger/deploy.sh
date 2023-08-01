#!/bin/bash

VM="badger"
COLLECTIONS=("dgg_national", "dgg_subnational")
DIR="/home/ubuntu/mySocialWatcher"

# cron
sudo cp ${DIR}/docker/collectors/${VM}/${VM}_crontab /etc/cron.d/

# config
cd ${DIR}
for COLLECTION in ${COLLECTIONS[@]};
do
  python3 config/collections/${COLLECTION}.py
done

# docker
cd ${DIR}/docker/collectors/${VM}
docker-compose up --build --no-start

unset VM
unset COLLECTIONS
unset DIR
