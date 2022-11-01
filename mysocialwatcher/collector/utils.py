import requests
import json
import gzip
import pandas as pd
from ast import literal_eval


def gunzip(source_filepath, dest_filepath, block_size=65536):
    """unzip .csv.gz files from pySocialWatcher"""
    with gzip.open(source_filepath, 'rb') as s_file, open(dest_filepath, 'wb') as d_file:
        while True:
            block = s_file.read(block_size)
            if not block:
                break
            else:
                d_file.write(block)


def submit_psw_csv(filename, token, platform, country='XX', valid=False,
                   url='http://10.131.129.27/api/v1/social_media_audience/write'):
    """Submit pysocialwatcher csv to /api/v1/fb/write"""

    # load data
    dat = pd.read_csv(filename)

    for index, row in dat.iterrows():

        # prepare json objects
        if row.get('response')[:2] == "b\'":
            fb_response_bytes = literal_eval(row.get('response'))
        else:
            fb_response_bytes = bytes(row.get('response'), encoding='utf-8')

        geo = literal_eval(row.get('geo_locations'))
        all_fields = {k: v for k, v in literal_eval(row.get('all_fields'))}
        targeting = literal_eval(row.get('targeting'))

        # remove apostrophe from geo_location name
        if geo['name'] in ['regions', 'cities'] and 'name' in list(geo['values'][0].keys()):
            geo_name = geo['values'][0]['name'].replace("'", '')
            geo['values'][0]['name'] = geo_name
            all_fields['geo_locations'] = geo
            targeting['geo_locations'][geo['name']][0]['name'] = geo_name

        # add country code if missing
        if geo['name'] in ['regions', 'cities']:
            country_list = []
            for i in range(len(geo.get('values'))):
                if 'country_code' in geo.get('values')[i].keys():
                    country_list.append(geo.get('values')[i].get('country_code'))
                else:
                    x = list(filter(lambda i:'country:' in i, geo.get('pySocialWatcherReference').split('; ')))
                    x = x[0].replace('country:', '')
                    country_list.append(x)
                    geo['values'][i]['country_code'] = x

            if len(set(country_list)) == 1:
                country = list(set(country_list))[0]
            else:
                dat.loc[index, 'row_index'] = int(index)
                dat.loc[index, 'status'] = 400
                dat.loc[index, 'message'] = 'Bad Request: Could not identify a single country.'
                next


        # prepare API arguments
        args = {'valid': valid,
                'token': token,
                'platform': platform,
                'country': country,
                'timestamp': row.get('timestamp'),
                'geo_locations': json.dumps(geo),
                'gender': row.get('genders'),
                'age_min': literal_eval(row.get('ages_ranges')).get('min'),
                'age_max': literal_eval(row.get('ages_ranges')).get('max'),
                'dau': row.get('dau_audience'),
                'mau': row.get('mau_audience'),
                'mau_upper': row.get('mau_audience_upper_bound'),
                'mau_lower': row.get('mau_audience_lower_bound'),
                'all_fields': json.dumps(all_fields),
                'targeting': json.dumps(targeting),
                'response': json.dumps(json.loads(fb_response_bytes.decode('utf-8')))
                }

        # drop arguments with no data
        drop = []
        for i in args.keys():
            if args.get(i) is None:
                drop.append(i)
            elif type(args.get(i)) == float and math.isnan(args.get(i)):
                drop.append(i)
        for i in drop:
            del args[i]

        response = requests.get(url=url, params=args)
        response = literal_eval(json.dumps(response.json()))

        dat.loc[index, 'row_index'] = int(index)
        dat.loc[index, 'timestamp'] = response.get('timestamp')
        dat.loc[index, 'status'] = int(response.get('status'))
        dat.loc[index, 'message'] = response.get('message')

    # return result
    result = dat[['row_index', 'timestamp', 'status', 'message']]
    return(result)
