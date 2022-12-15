#!/bin/bash

# backup directory
backup_dir=/research/backup/psw_datahub/$(date +"%Y%m%d")

# make directory
mkdir ${backup_dir}

# remote dump
pg_dump -h 18.135.72.18 -U postgres -Fc social_media_audience > ${backup_directory}/social_media_audience.dump

# cleanup
unset backup_dir
