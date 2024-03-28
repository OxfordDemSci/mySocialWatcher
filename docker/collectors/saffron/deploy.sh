#!/bin/bash

VM="saffron"
COLLECTIONS=("ukraine_countries" "ukraine_europe" "ukraine_language" "ukraine_neighbours" "ukraine_regions", "ukraine_admin2_tesselation_interior","ukraine_admin2_tesselation_exterior")
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
docker-compose up --build --no-start

unset VM
unset COLLECTIONS
unset DIR
