#!/bin/bash

cd /app

for file in specs/specs*.json
do
  python3 utils/kill.py
  python3 main.py $file
done
