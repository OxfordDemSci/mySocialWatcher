# Dockerfile used by the datahub_api
FROM python:3.10-slim-bookworm

WORKDIR /app

RUN apt-get update -y
RUN apt-get -y install libpq-dev gcc gdal-bin libgdal-dev
RUN pip install psycopg2-binary

COPY docker/datahub/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY mysocialwatcher mysocialwatcher
# COPY mysocialwatcher/api/gunicorn_config.py gunicorn_config.py
COPY mysocialwatcher/api/wsgi.py wsgi.py

CMD [ "gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]

# CMD ["sleep", "3600"]