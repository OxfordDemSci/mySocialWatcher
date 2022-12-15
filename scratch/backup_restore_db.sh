#!/bin/bash

# ---- backup database ---- #

# ssh to psw_datahub virtual machine
ssh psw_datahub

# execute dump inside container
docker exec -it datahub_db pg_dump -U postgres -Fc social_media_audience > /social_media_audience.dump

# get container hash
docker inspect datahub_db

# copy dump to host
docker cp [container_hash]:/social_media_audience.dump ~/social_media_audience.dump

# logout of psw_datahub virtual machine
exit

# copy dump to local machine
mkdir /research/backup/psw_datahub/[current_date]
scp datahub_psw:~/social_media_audience.dump /research/backup/psw_datahub/[current_date]


# ---- restore database ---- #

# copy dump to psw_datahub virtual machine
scp /research/backup/psw_datahub/[current_date]/social_media_audience.dump datahub_psw:~/

# get container hash
docker inspect datahub_db

# copy dump to host
docker cp ~/social_media_audience.dump [container_hash]:/social_media_audience.dump

# login to container shell
docker exec -it datahub_db bash

# delete existing database
su postgres
dropdb social_media_audience

# restore from dump
pg_restore -U postgres -C -d postgres /social_media_audience.dump