#!/bin/bash

# config
cd ~/mySocialWatcher
python3 config/collections/rus_exodus_facebook.py
python3 config/collections/rus_exodus_instagram.py

# cron
cd ~/mySocialWatcher/collectors/mingo
sudo cp mingo_crontab /etc/cron.d/

# docker
cd ~/mySocialWatcher/collectors/mingo
docker-compose up -d
