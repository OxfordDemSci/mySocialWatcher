# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

# install packages
RUN apt-get update
RUN apt-get install -y cron
RUN apt-get install -y curl
RUN apt-get install -y git
RUN apt-get install -y procps

# Add Tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

# install python packages
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# install pysocialwatcher and mysocialwatcher
COPY pysocialwatcher pysocialwatcher
COPY mysocialwatcher mysocialwatcher
COPY mysocialwatcher/collector/main.py main.py
COPY docker/collectors/_utils utils

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
#ENTRYPOINT ["/bin/bash", "-c"]
ENTRYPOINT ["/tini", "--"]

# CMD ["/bin/bash", "-c", "./utils/launch.sh; cron -f"]
CMD ["/bin/bash", "-c", "./utils/launch.sh"]
