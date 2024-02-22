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

# install mysocialwatcher
COPY mysocialwatcher mysocialwatcher
COPY mysocialwatcher/crawler/main.py main.py

# commmand
# ENTRYPOINT ["/bin/sh", "-c"]
CMD ["python3", "./main.py"]

# CMD ["tail", "-f", "/dev/null"]
