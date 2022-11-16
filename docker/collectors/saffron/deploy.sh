#!/bin/bash

# config
cd ~/mySocialWatcher
python3 config/collections/ukraine_countries.py
python3 config/collections/ukraine_europe.py
python3 config/collections/ukraine_language.py
python3 config/collections/ukraine_neighbours1.py
python3 config/collections/ukraine_neighbours2.py
python3 config/collections/ukraine_regions.py

# cron
cd ~/mySocialWatcher/collectors/saffron
sudo cp saffron_crontab /etc/cron.d/

# docker
cd ~/mySocialWatcher/collectors/saffron
docker-compose up -d
