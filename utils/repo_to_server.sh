#!/bin/bash

# command line arguments
server=$1

# sub-folders to copy
folders=("config" "docker" "utils" "mysocialwatcher" "pysocialwatcher")

for folder in ${folders[@]};
do
  scp -r ./$folder $server:~/mySocialWatcher/
done

# files to copy
files=("README.md" "requirements.txt")

for file in ${files[@]};
do
  scp ./$file $server:~/mySocialWatcher/
done

