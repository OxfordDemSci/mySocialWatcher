import os
import json
import math
import logging
import datetime
import requests
import sqlalchemy
from ast import literal_eval
from dotenv import load_dotenv

# environment variables
load_dotenv('docker/datahub/_utils/migrate_old_db.env')
api_url = os.environ.get('api_url')
jiani_token = os.environ.get('jiani_token')
ian_token = os.environ.get('ian_token')
doug_token = os.environ.get('doug_token')

# logging
log_dir = os.path.join('data', 'datahub_migrate')
os.makedirs(log_dir, exist_ok=True)
start_time = datetime.datetime.now()
logging.basicConfig(
    filename=os.path.join(log_dir, start_time.strftime('%Y%m%d_%H%M%S') + '.log'),
    format='%(asctime)s (%(levelname)s) - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.WARNING)


def timestamp_str():
    return '[' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] '


def print_progress(i, n):
    if i in range(0, int(n), int(n/100)):
        print(timestamp_str() + ' ... row ' + str(i) + ' (' + str(round(i / n * 100)) + '%)')


def write_row(row, table, token, collection=None, valid=False):

    # prepare API arguments
    args = {'token': token,
            'collection': collection,
            'valid': valid,
            'platform': table,
            # 'contributed_on': row.get('contributed_on').isoformat(),
            # 'country': row.get('country'),
            'timestamp': row.get('timestamp'),
            'gender': row.get('gender'),
            'age_min': row.get('age_min'),
            'age_max': row.get('age_max'),
            'dau': row.get('dau'),
            'mau': row.get('mau'),
            'mau_upper': row.get('mau_upper'),
            'mau_lower': row.get('mau_lower'),
            'geo_locations': json.dumps(row.get('geo_locations')),
            'all_fields': json.dumps(row.get('all_fields')),
            'targeting': json.dumps(row.get('targeting')),
            'response': json.dumps(row.get('response'))
            }

    # drop arguments with no data
    drop = []
    for i in args.keys():
        if args.get(i) is None:
            drop.append(i)
        elif isinstance(args.get(i), float) and math.isnan(args.get(i)):
            drop.append(i)
        elif args.get(i) == '{}':
            drop.append(i)
    for i in drop:
        del args[i]

    # submit api request
    response = None
    try:
        response = requests.get(url=api_url, params=args)
        response = literal_eval(json.dumps(response.json()))

        if response.get('status') in [200, 409]:
            logger.info(str(response))
        else:
            logger.warning(str(response))

    except Exception as e:
        logger.error(str(e))

    return response


if __name__ == '__main__':

    # database connection
    engine = sqlalchemy.create_engine('postgresql+psycopg2://reader:pass@localhost:5432/social_media_audience',
                                      poolclass=sqlalchemy.pool.NullPool)

    # # Jiani's Facebook collections for DGG
    # with engine.connect() as conn:
    #     # conn = engine.connect()
    #
    #     logger.info(timestamp_str() + 'Migrating Jiani\'s collections...')
    #     print(timestamp_str() + 'Migrating Jiani\'s collections...')
    #
    #     sql = 'select * from facebook where contributor_id = 4 order by timestamp desc, country asc;'
    #     result = conn.execute(sql)
    #
    #     row_idx = 0
    #     for row in result.mappings():
    #         row_idx += 1
    #         print_progress(row_idx, 4094751)
    #
    #         response = write_row(row,
    #                              table='facebook',
    #                              collection='dgg_national',
    #                              token=jiani_token,
    #                              valid=True)
    #         # if row_idx > 10:
    #         #     break
    #
    #     logger.info(timestamp_str() + 'Finished migrating Jiani\'s collections.')
    #     print(timestamp_str() + 'Finished migrating Jiani\'s collections.')

    # # Ian's Facebook collections for DGG
    # with engine.connect() as conn:
    #     # conn = engine.connect()
    #
    #     logger.info('Migrating Ian\'s collections...')
    #
    #     sql = 'select * from facebook where contributor_id = 3;'
    #     result = conn.execute(sql)
    #
    #     row_idx = 0
    #     for row in result.mappings():
    #         row_idx += 1
    #         response = write_row(row,
    #                              table='facebook',
    #                              collection='dgg_national',
    #                              token=ian_token,
    #                              valid=True)
    #
    #     logger.info('Finished migrating Ian\'s collections.')

    # Ukraine regions
    with engine.connect() as conn:
        # conn = engine.connect()

        logger.info(timestamp_str() + 'Migrating Ukraine regional collections...')
        print(timestamp_str() + 'Migrating Ukraine regional collections...')

        sql = "select * from facebook where contributor_id =1 and country='UA' and geo_locations ->> 'name' = 'regions';"
        result = conn.execute(sql)

        row_idx = 0
        for row in result.mappings():
            row_idx += 1
            print_progress(row_idx, 1300668)

            response = write_row(row,
                                 table='facebook',
                                 collection='ukraine_regions',
                                 token=doug_token,
                                 valid=True)
            # if row_idx > 10:
            #     break

        logger.info(timestamp_str() + 'Finished migrating Ukraine regions collections.')
        print(timestamp_str() + 'Finished migrating Ukraine regions collections.')

