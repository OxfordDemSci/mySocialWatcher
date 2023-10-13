#!/bin/bash

# command line arguments
data_dir=$1

# find logs directories
logs=$(find $data_dir -name "*.log" -type f -newerct 'yesterday' -print)

for log in $logs;
do
  echo ''
  echo '============================================================================'
  echo $log
  echo '============================================================================'
  head $log
  echo '[...]'
  tail -n 20 $log
  read -p 'Press any key to continue to next log...'
done
