#!/bin/bash

cd /app

echo "`date`: Collections launched." >> data/launch.log

for file in specs/specs*.json
do

  echo "`date`: Started ${file}..." >> data/launch.log
  python3 utils/kill.py
  python3 main.py $file
  echo "`date`: Completed ${file}." >> data/launch.log

done

echo "`date`: All collections finished." >> data/launch.log
