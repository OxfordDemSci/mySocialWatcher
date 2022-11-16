#!/bin/bash

# config
cd ~/mySocialWatcher
python3 config/collections/dgg_national.py

# cron
sudo cp ~/mySocialWatcher/collectors/badger/badger_crontab /etc/cron.d/

# docker
cd ~/mySocialWatcher/collectors/badger
docker-compose up -d --build
