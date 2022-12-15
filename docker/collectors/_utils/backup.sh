#!/bin/bash

# # create new backup directory
# backup_dir=/research/backup/psw_collectors/$(date +"%Y%m%d")
# mkdir ${backup_dir}

# update old backup directory
backup_dir=/research/backup/psw_collectors/20221215/

# sync remote files to backup directory
rsync -avhz psw_collectors:~/mySocialWatcher/data/ ${backup_dir}

# cleanup
unset backup_dir
