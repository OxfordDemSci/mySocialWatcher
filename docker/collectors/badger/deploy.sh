#!/bin/bash


VM="badger"
COLLECTIONS=("dgg_national" "dgg_national_ins" "dgg_national_home_recent" "dgg_subnational_age"
             "dgg_subnational_education" "dgg_subnational_device" "dgg_subnational_age_device"
              "dgg_subnational_age_education" "dgg_subnational_tessellated_age" "dgg_subnational_tessellated_device"
              "dgg_subnational_FB_key_device" "dgg_subnational_FB_key_age")


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
