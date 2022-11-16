#!/bin/bash

# config
cd ~/mySocialWatcher
python3 config/collections/dgg_national.py

# cron
sudo cp ~/mySocialWatcher/docker/collectors/badger/badger_crontab /etc/cron.d/

# docker
cd ~/mySocialWatcher/docker/collectors/badger
docker-compose up -d --build
