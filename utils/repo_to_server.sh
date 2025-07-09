#!/bin/bash

# command line arguments
local_folder=$1
remote_folder=$2

# rsync folder
rsync -rvhe ssh --exclude-from='./utils/repo_to_server_exclude.txt' $local_folder $remote_folder
