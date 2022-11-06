import os
import requests
import json
import math
import pandas as pd
from ast import literal_eval
from dotenv import load_dotenv

# environment variables
load_dotenv()
load_dotenv('./config/private/collector.env')


def country_from_geo(geo):

    country = []

    if geo['name'] == 'countries':
        country.append(geo['values'][0])

    elif geo['name'] in ['regions', 'cities']:

        if 'country_code' in geo.get('values')[0].keys():
            country += [geo.get('values')[i].get('country_code') for i in range(len(geo.get('values')))]
        elif 'PySocialWatcherReference' in geo.keys():
            for i in range(len(geo.get('values'))):
                x = list(filter(lambda i: 'country:' in i, geo.get('pySocialWatcherReference').split('; ')))
                x = x[0].replace('country:', '')
                country.append(x)
                geo['values'][i]['country_code'] = x

    return list(set(country))


def submit_psw_csv(filename, token,
                   valid=False,
                   url='http://127.0.0.1/api/v1/social_media_audience/write'):
    """Submit pysocialwatcher csv to /api/v1/fb/write"""

    # load data
    dat = pd.read_csv(filename)

    for index in range(len(dat)):

        row = dat.iloc[index]

        # ---- platform ---- #
        platform = literal_eval(row['publisher_platforms'])

        if len(platform) > 1:
            next
        else:
            platform = platform[0]

        # ---- all_fields ---- #
        all_fields = {k: v for k, v in literal_eval(row.get('all_fields'))}

        # ---- targeting ---- #
        targeting = literal_eval(row.get('targeting'))

        # ---- response ----#
        if row.get('response')[:2] == "b\'":
            response_bytes = literal_eval(row.get('response'))
        else:
            response_bytes = bytes(row.get('response'), encoding='utf-8')

        response = json.loads(response_bytes.decode('utf-8'))

        # ---- prepare: geo_locations ----#
        geo = all_fields['geo_locations']  # literal_eval(row.get('geo_locations'))

        # ---- country ----#
        country = country_from_geo(geo)

        if len(country) == 1:
            country = country[0]
        else:
            dat.loc[index, 'row_index'] = index
            dat.loc[index, 'status'] = 400
            dat.loc[index, 'message'] = 'Bad Request: Could not identify a single country.'
            next

        # prepare API arguments
        args = {'valid': valid,
                'token': token,
                'platform': platform,
                'country': country,
                'timestamp': row.get('timestamp'),
                'gender': row.get('genders'),
                'age_min': all_fields.get('ages_ranges').get('min'),
                'age_max': all_fields.get('ages_ranges').get('max'),
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
        response = requests.get(url=url, params=args)
        response = literal_eval(json.dumps(response.json()))

        # format results
        dat.loc[index, 'row_index'] = int(index)
        dat.loc[index, 'timestamp'] = response.get('timestamp')
        dat.loc[index, 'status'] = int(response.get('status'))
        dat.loc[index, 'message'] = response.get('message')

    # return result
    result = dat[['row_index', 'timestamp', 'status', 'message']]

    return result


def crawler(crawl_dir, token,
            url='http://127.0.0.1/api/v1/social_media_audience/write'):
    # crawl_dir = 'data/_test'

    # file list
    file_list = []
    for (root, dirs, file) in os.walk(crawl_dir):
        for f in file:
            full_path = os.path.join(root, f)
            if "finished/dataframe_collected_finished_" in full_path and os.path.splitext(f)[1] == '.csv':
                file_list.append(full_path)
        for f in file:
            if "collecting/dataframe_collecting_" in full_path and os.path.splitext(f)[1] == '.csv':
                file_list.append(full_path)

    for file in file_list:

        # write collection to SQL via API
        response = submit_psw_csv(
            filename=file,
            url=url,
            token=token,
            valid=True)

        collect_info = os.path.basename(file).\
            replace('dataframe_collecting_', '').\
            replace('dataframe_collected_finished_', '').\
            replace('.csv', '')

        # save API responses
        response.to_csv(os.path.join('data', 'logs', collect_info + '_api.csv'))


if __name__ == "__main__":

    crawler(crawl_dir='./data',
            token=os.environ.get('API_TOKEN'),
            url=os.environ.get('API_URL'))
