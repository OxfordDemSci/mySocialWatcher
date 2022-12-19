#!/bin/bash

# backup directory
backup_path=/research/backup/psw_datahub/$(date +"%Y%m%d")/social_media_audience.dump

# # drop database
# dropdb -h 18.135.72.18 --username=postgres social_media_audience

# remote restore from dump
pg_restore --host=18.135.72.18 --username=postgres --dbname=postgres --password --clean --create ${backup_path}

# cleanup
unset backup_path
