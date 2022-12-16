#!/bin/bash

# define variables
base_dir=/research/backup/psw_collectors
past_backups=($(ls ${base_dir}))
current_date=$(date +"%Y%m%d")
last_backup=${past_backups[-1]}

# check time since last fresh backup
let diff_backup=(`date +%s -d ${current_date}`-`date +%s -d ${last_backup}`)/86400
printf "\n${diff_backup} days since last fresh backup...\n"

# define backup directory
if [ $diff_backup -le 7 ]; then
  printf "    updating existing backup directory: ${last_backup}\n\n"
  backup_dir=${base_dir}/${last_backup}
else
  printf "    creating new backup directory: ${current_date}\n\n"
  backup_dir=${base_dir}/${current_date}
  mkdir -p ${backup_dir}
fi

# sync remote files to backup directory
rsync -avhz psw_collectors:~/mySocialWatcher/data/ ${backup_dir} --delete
printf "\n"

# delete backups older than 90 days
for i in "${past_backups[@]}"
do
  let x=(`date +%s -d ${current_date}`-`date +%s -d ${i}`)/86400
  if [ $x -ge 90 ]; then
    printf "Deleting backup that is ${x} days old: ${i}\n"
    rm -R ${base_dir}/${i}
  fi
done
unset x; unset i
printf "\n"

# cleanup
unset base_dir
unset backup_dir
unset current_date
unset past_backups
unset last_backup
