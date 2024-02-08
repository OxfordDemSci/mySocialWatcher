#!/bin/bash

# copy .env
cp ~/mySocialWatcher/config/private/datahub.env ~/mySocialWatcher/docker/datahub/.env

# change mountpoint of docker volume
# https://stackoverflow.com/questions/63873956/change-mountpoint-of-docker-volume-to-a-custom-directory
# https://www.guguweb.com/2019/02/07/how-to-move-docker-data-directory-to-another-location-on-ubuntu/
sudo service docker stop

echo '{' >> /etc/docker/daemon.json
echo '  "data-root": "/disk/docker' >> /etc/docker/daemon.json
echo '}' >> /etc/docker/daemon.json

sudo service docker start

# deploy datahub
cd ~/mySocialWatcher/docker/datahub
docker-compose up -d --build
