FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY mysocialwatcher mysocialwatcher
COPY mysocialwatcher/api/gunicorn_config.py gunicorn_config.py
COPY mysocialwatcher/api/wsgi.py wsgi.py

CMD [ "gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]