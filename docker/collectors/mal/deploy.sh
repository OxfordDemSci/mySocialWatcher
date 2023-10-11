#!/bin/bash

VM="mal"
COLLECTIONS=("dgg_national_ins")
DIR="/home/ubuntu/mySocialWatcher"

# config
cd ${DIR}
for COLLECTION in ${COLLECTIONS[@]};
do
  python3 config/collections/${COLLECTION}.py
done

# docker
cd ${DIR}/docker/collectors/${VM}
docker-compose up --build --no-start

# cron
cd ${DIR}
sudo cp ${DIR}/docker/collectors/${VM}/${VM}_crontab /etc/cron.d/

unset VM
unset COLLECTIONS
unset DIR
