# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

# install packages
RUN apt-get update
RUN apt-get install -y cron
RUN apt-get install -y curl
RUN apt-get install -y git
RUN apt-get install -y procps

# install pySocialWatcher
WORKDIR /app
COPY pysocialwatcher pysocialwatcher
COPY setup.py setup.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN python3 setup.py install

# install mySocialWatcher
COPY mysocialwatcher mysocialwatcher
COPY mysocialwatcher/main.py main.py
COPY ./deploy/utils utils

# collection config
ARG collection_dir=${collection_dir}
COPY $collection_dir/credentials.csv credentials.csv
COPY $collection_dir/.env .env
COPY $collection_dir/specs specs
COPY $collection_dir/cronjob /etc/cron.d/cronjob

# chmod executables
RUN chmod 0744 ./utils/launch.sh
RUN chmod 0744 ./utils/cleanup.sh

# cron
RUN chmod 0644 /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob

# commmand
ENTRYPOINT ["./utils/launch.sh", "&", "cron", "-f"]
