#!/bin/bash

# environment
cp ~/mySocialWatcher/config/private/crawler.env ~/mySocialWatcher/docker/crawler/.env

# cron
cd ~/mySocialWatcher/docker/crawler
sudo cp crawler_crontab /etc/cron.d/

# docker
cd ~/mySocialWatcher/docker/crawler
docker-compose up -d
