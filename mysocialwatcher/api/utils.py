import os
import datetime
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


def timestr():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0).isoformat(sep=" ")[:-3]


def conn_to_database(mode='r'):

    if mode == 'w':
        user = 'api_writer'
        pw = os.environ.get('POSTGRES_WPASS')
    else:
        user = 'api_reader'
        pw = os.environ.get('POSTGRES_RPASS')

    conn = psycopg2.connect(host=os.environ.get('POSTGRES_HOST'),
                            database=os.environ.get('POSTGRES_DB'),
                            user=user,
                            password=pw)

    # conn = create_engine('postgresql+psycopg2://' + \
    #                      user + ':' + \
    #                      pw + '@' + \
    #                      os.environ.get('POSTGRES_HOST') + '/' + \
    #                      os.environ.get('POSTGRES_DB'))

    return conn
