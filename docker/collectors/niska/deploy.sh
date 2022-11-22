#!/bin/bash

VM="niska"
COLLECTIONS=("venezuelan_exodus1" "venezuelan_exodus2")
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
