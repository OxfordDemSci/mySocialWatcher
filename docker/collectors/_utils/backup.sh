#!/bin/bash

# define variables
base_dir=~/ndph/J/backup/psw_collectors
past_backups=($(ls ${base_dir}))
current_date=$(date +"%Y%m%d")
last_backup=${past_backups[-1]}

# check time since last fresh backup
let diff_backup=(`date +%s -d ${current_date}`-`date +%s -d ${last_backup}`)/86400

# define backup directory
if [ $diff_backup -le 7 ]; then
  backup_dir=${base_dir}/${last_backup}
else
  backup_dir=${base_dir}/${current_date}
  mkdir -p ${backup_dir}
fi


# initialise log file
log_file=${backup_dir}/log.txt
printf "[`date +'%Y-%m-%d %H:%M:%S'`] ${backup_dir}\n" >> ${log_file}


# sync remote files to backup directory
rsync -avhz psw_collectors:~/mySocialWatcher/data/ ${backup_dir} --delete --exclude log.txt
printf "[`date +'%Y-%m-%d %H:%M:%S'`] Sync completed\n" >> ${log_file}


# delete backups older than 90 days
for i in "${past_backups[@]}"
do
  let x=(`date +%s -d ${current_date}`-`date +%s -d ${i}`)/86400
  if [ $x -ge 90 ]; then
    printf "[`date +'%Y-%m-%d %H:%M:%S'`] Deleting backup (${x} days old): ${i}\n" >> ${log_file}
    rm -R ${base_dir}/${i}
  fi
done
unset x; unset i


# cleanup
unset base_dir
unset backup_dir
unset current_date
unset past_backups
unset last_backup

printf "\n" >> ${log_file}
