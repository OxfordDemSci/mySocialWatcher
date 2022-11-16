# syntax=docker/dockerfile:1
FROM python:slim-buster

# install packages
RUN apt-get update

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
