#!/bin/bash

# config
cd ~/mySocialWatcher
python3 config/collections/venezuelan_exodus1.py
python3 config/collections/venezuelan_exodus2.py

# cron
sudo cp ~/mySocialWatcher/collectors/niska/niska_crontab /etc/cron.d/

# docker
cd ~/mySocialWatcher/collectors/niska
docker-compose up -d --build
