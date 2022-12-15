#!/bin/bash

# backup directory
backup_dir=/research/backup/psw_datahub/$(date +"%Y%m%d")

# remote restore from dump
pg_restore -h 18.135.72.18 -U postgres -C -d postgres ${backup_dir}/social_media_audience.dump

# cleanup
unset backup_date
