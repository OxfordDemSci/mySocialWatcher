#!/bin/bash

# environment
cp ~/mySocialWatcher/config/private/crawler.env ~/mySocialWatcher/docker/crawler/.env

# cron
sudo cp ~/mySocialWatcher/docker/crawler/crawler_crontab /etc/cron.d/

# docker
cd ~/mySocialWatcher/docker/crawler
docker-compose up -d --build

# if you want to run docker compose with replicas
# docker-compose --compatibility up -d --build