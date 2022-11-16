#!/bin/bash

# config
cd ~/mySocialWatcher
python3 config/collections/rus_exodus_facebook.py
python3 config/collections/rus_exodus_instagram.py

# cron
sudo cp ~/mySocialWatcher/collectors/mingo/mingo_crontab /etc/cron.d/

# docker
cd ~/mySocialWatcher/collectors/mingo
docker-compose up -d --build
