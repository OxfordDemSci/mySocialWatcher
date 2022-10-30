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

# cron
RUN chmod 0644 /etc/cron.d/cronjob && crontab /etc/cron.d/cronjob

# # commmand
# ENTRYPOINT ["cron", "-f;", "source", "utils/lanuch.sh"]
