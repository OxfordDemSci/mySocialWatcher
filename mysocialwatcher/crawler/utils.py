import os
import requests
import json
import math
import datetime
import warnings
from time import sleep
import pandas as pd
from ast import literal_eval


# def country_from_geo(geo):
#
#     country = []
#
#     if geo['name'] == 'countries':
#         country.append(geo['values'][0])
#
#     elif geo['name'] in ['regions', 'cities']:
#
#         if 'country_code' in geo.get('values')[0].keys():
#             country += [geo.get('values')[i].get('country_code') for i in range(len(geo.get('values')))]
#         elif 'PySocialWatcherReference' in geo.keys():
#             for i in range(len(geo.get('values'))):
#                 x = list(filter(lambda i: 'country:' in i, geo.get('pySocialWatcherReference').split('; ')))
#                 x = x[0].replace('country:', '')
#                 country.append(x)
#                 geo['values'][i]['country_code'] = x
#
#     return list(set(country))


def psw_to_sql(df, collection_name, token,
               valid=False,
               url='http://127.0.0.1/api/v1/write'):
    """Submit pysocialwatcher csv to /api/v1/fb/write"""

    for index in range(len(df)):
        # index = 0

        row = df.iloc[index]

        # ---- platform ---- #
        platform = literal_eval(row['publisher_platforms'])

        if len(platform) > 1:
            warnings.warn(f'More than one platform detected at index {index}.')
            continue
        else:
            platform = platform[0]

        # ---- all_fields ---- #
        all_fields = {k: v for k, v in literal_eval(row.get('all_fields'))}

        # ---- targeting ---- #
        targeting = literal_eval(row.get('targeting'))

        # ---- response ----#
        response = row.get('response')
        if response[0] == "{":
            response = json.loads(row.get('response'))
        elif response[0] == '[':
            response = literal_eval(row.get('response'))
        elif response[:2] == "b\'":
            response = json.loads(literal_eval(row.get('response')).decode('utf-8'))

        # ---- prepare: geo_locations ----#
        geo = all_fields['geo_locations']  # literal_eval(row.get('geo_locations'))

        # # ---- country ----#
        # country = countries_from_geo_locations(geo)
        #
        # if len(country) == 1:
        #     country = country[0]
        # else:
        #     df.loc[index, 'timestamp_api'] = str(datetime.datetime.now())
        #     df.loc[index, 'status_api'] = 400
        #     df.loc[index, 'message_api'] = 'Bad Request: Could not identify a single country.'
        #     next

        # ---- age ---- #
        ages_ranges = literal_eval(row.get('ages_ranges'))
        if isinstance(ages_ranges, dict):
            age_min = ages_ranges.get('min')
            age_max = ages_ranges.get('max')
        elif isinstance(ages_ranges, list):
            age_min = ages_ranges[0]
            age_max = ages_ranges[1]

        # ---- prepare API arguments ---- #
        args = {'valid': valid,
                'collection': collection_name,
                'token': token,
                'platform': platform,
                # 'country': country,
                'timestamp': row.get('timestamp'),
                'gender': row.get('genders'),
                'age_min': age_min,
                'age_max': age_max,
                'dau': row.get('dau_audience'),
                'mau': row.get('mau_audience'),
                'mau_upper': row.get('mau_audience_upper_bound'),
                'mau_lower': row.get('mau_audience_lower_bound'),
                'geo_locations': json.dumps(geo),
                'all_fields': json.dumps(all_fields),
                'targeting': json.dumps(targeting),
                'response': json.dumps(response)
                }

        # drop arguments with no data
        drop = []
        for i in args.keys():
            if args.get(i) is None:
                drop.append(i)
            elif isinstance(args.get(i), float) and math.isnan(args.get(i)):
                drop.append(i)
        for i in drop:
            del args[i]

        # submit api request
        http_response = ''
        try:
            # response = requests.get(url=url, params=args)
            http_response = requests.post(url=url, data=args)
            http_response_dict = json.loads(json.dumps(http_response.json()))

            df.loc[index, 'timestamp_api'] = http_response_dict.get('timestamp')
            df.loc[index, 'status_api'] = int(http_response_dict.get('status'))
            df.loc[index, 'message_api'] = http_response_dict.get('message')

        except Exception as e:
            if isinstance(http_response, requests.models.Response):
                http_response_text = http_response.text
            else:
                http_response_text = str(http_response)

            message = 'EXCEPTION: "' + str(e) + '";\n HTTP RESPONSE: "' + http_response_text + '"'
            warnings.warn(message)
            df.loc[index, 'timestamp_api'] = str(datetime.datetime.now())
            df.loc[index, 'status_api'] = 500
            df.loc[index, 'message_api'] = message

    # return result
    return df[['timestamp_api', 'status_api', 'message_api']]
    # return df


def governor(func, hours=1):
    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()

        func(*args, **kwargs)

        # sleep if crawl was less than an hour
        time_diff = datetime.datetime.now() - start_time
        sleep_time = datetime.timedelta(hours=hours) - time_diff
        if sleep_time.seconds > 0:
            print('[' + str(datetime.datetime.now()) + '] Sleeping for ' + str(sleep_time))
            sleep(sleep_time.seconds)

    return wrapper


def crawler(data_dir, token, url='http://127.0.0.1/api/v1/write'):
    # crawl_dir = 'data/_test'

    print('-----------------------------')
    print('[' + str(datetime.datetime.now()) + '] Starting crawler...')

    data_dir = os.path.abspath(data_dir.rstrip('/'))
    crawl_dir = os.path.join(data_dir, 'crawler')
    os.makedirs(crawl_dir, exist_ok=True)

    # file list
    file_list = []
    exclude_dirs = ['crawler', 'db-data']
    for (root, dirs, file) in os.walk(data_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in file:
            full_path = os.path.join(root, f)
            if "finished/dataframe_collected_finished_" in full_path:
                file_list.append(full_path)

    # ---- finished ---- #
    for file in file_list:
        # file = file_list[0]
        # file = './data/_test/_test/finished/dataframe_collected_finished_specs001_20221106.csv'

        out_path = file.replace(data_dir, crawl_dir).replace('.csv.gz', '_log.csv.gz')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        if not os.path.exists(out_path):

            print('[' + str(datetime.datetime.now()) + '] ' + file)

            # load data
            df = pd.read_csv(file)
            collection_name = file.split('/')[-3].lstrip('_')

            # write collection to SQL via API
            response = psw_to_sql(
                df=df,
                collection_name=collection_name,
                url=url,
                token=token,
                valid=True)

            # save API responses
            response.to_csv(out_path)

    print('[' + str(datetime.datetime.now()) + '] Crawler finished.')
