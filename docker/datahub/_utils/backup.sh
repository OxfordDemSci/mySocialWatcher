#!/bin/bash

# backup directory
base_dir=/research/backup/psw_datahub
past_backups=($(ls ${base_dir}))
current_date=$(date +"%Y%m%d")
backup_dir=${base_dir}/${current_date}
dump_file=${backup_dir}/social_media_audience.dump

# message to console
printf "Preparing: ${dump_file}\n"

# make directory
mkdir -p ${backup_dir}

# remote dump
pg_dump -h 18.135.72.18 -U postgres -Fc social_media_audience > ${dump_file}

# compress
printf "Compressing (gzip)\n"
gzip -f ${dump_file}

# delete backups older than 90 days
for i in "${past_backups[@]}"
do
  let x=(`date +%s -d ${current_date}`-`date +%s -d ${i}`)/86400
  if [ $x -ge 90 ]; then
    printf "Deleting backup that is ${x} days old: ${i}\n"
    rm -R ${base_dir}/${i}
  fi
done

printf "\n"
unset x; unset i


# cleanup
unset backup_dir
