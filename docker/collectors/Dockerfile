# syntax=docker/dockerfile:1
FROM python:3.10-slim-buster

# install packages
RUN apt-get update
RUN apt-get -y install libpq-dev gcc
RUN pip install psycopg2-binary

# install python packages
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# install pysocialwatcher and mysocialwatcher
COPY pysocialwatcher pysocialwatcher
COPY mysocialwatcher mysocialwatcher
COPY mysocialwatcher/collector/main.py main.py
COPY docker/collectors/_utils utils
COPY utils/collectors_cleanup.sh ./utils/cleanup.sh

RUN chmod 0744 ./utils/launch.sh
RUN chmod 0744 ./utils/cleanup.sh

# collection config
RUN ln -s in/credentials.csv credentials.csv
RUN ln -s in/specs specs
#RUN ln -s in/.env .env

# define sleep time
ARG sleep_time
RUN if [$sleep_time = '']; then echo sleep_time=11 >> .env; else echo sleep_time=$sleep_time >> .env; fi

# commmand
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["./utils/launch.sh"]

#CMD ["tail", "-f", "/dev/null"]