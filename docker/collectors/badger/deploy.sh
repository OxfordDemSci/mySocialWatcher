#!/bin/bash

# config
cd ~/mySocialWatcher
python3 config/collections/dgg_national.py

# cron
cd ~/mySocialWatcher/collectors/badger
sudo cp badger_crontab /etc/cron.d/

# docker
cd ~/mySocialWatcher/collectors/badger
docker-compose up -d --build
