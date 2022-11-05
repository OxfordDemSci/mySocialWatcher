# syntax=docker/dockerfile:1
FROM python:slim-buster

# install packages
RUN apt-get update

# install python packages
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# install pysocialwatcher and mysocialwatcher
COPY pysocialwatcher pysocialwatcher
COPY mysocialwatcher mysocialwatcher
COPY mysocialwatcher/collector/main.py main.py
COPY docker/collectors/_utils utils

RUN chmod 0744 ./utils/launch.sh
RUN chmod 0744 ./utils/cleanup.sh

# collection config
ARG collection_dir=${collection_dir}
COPY $collection_dir/credentials.csv credentials.csv
COPY $collection_dir/.env .env
COPY $collection_dir/specs specs

# commmand
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["./utils/launch.sh"]
