#!/bin/bash

# backup directory
base_dir=/research/backup/psw_datahub
past_backups=($(ls ${base_dir}))
current_date=$(date +"%Y%m%d")
backup_dir=${base_dir}/${current_date}
dump_file=${backup_dir}/social_media_audience.dump

# make directory
mkdir -p ${backup_dir}

# initialise log file
log_file=${backup_dir}/log.txt
printf "[`date +'%Y-%m-%d %H:%M:%S'`] ${dump_file}\n" >> ${log_file}

# remote dump
pg_dump -h 18.135.72.18 -U postgres -Fc social_media_audience > ${dump_file}

# compress
printf "[`date +'%Y-%m-%d %H:%M:%S'`] Compressing (gzip)\n" >> ${log_file}
gzip -f ${dump_file}

# delete backups older than 365 days
for i in "${past_backups[@]}"
do
  let x=(`date +%s -d ${current_date}`-`date +%s -d ${i}`)/86400
  if [ $x -ge 365 ]; then
    printf "[`date +'%Y-%m-%d %H:%M:%S'`] Deleting backup (${x} days old): ${i}\n" >> ${log_file}
    rm -R ${base_dir}/${i}
  fi
done


# cleanup
unset x; unset i
unset backup_dir

printf "[`date +'%Y-%m-%d %H:%M:%S'`] Completed\n\n" >> ${log_file}
