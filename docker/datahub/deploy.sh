#!/bin/bash

# copy .env
cp ~/mySocialWatcher/config/private/datahub.env ~/mySocialWatcher/docker/datahub/.env

# deploy datahub
cd ~/mySocialWatcher/docker/datahub
docker-compose up -d
