import pandas as pd
from ast import literal_eval
import json
import warnings
import math
import datetime
import requests
from mysocialwatcher.api.utils import check_args
from mysocialwatcher.api.utils import countries_from_geo_locations


# load problem data
file = '/research/git/OxfordDemSci/mySocialWatcher/data/test/test/finished/dataframe_collected_finished_MU_country_and_gadm1_part_1_20240224_betterestimate.csv'
df = pd.read_csv(file)

# ---- SIMULATION ----#

# select problem row
index = 10
row = df.iloc[index]

# -- CRAWLER --#

# arguments
collection_name = 'test_collection'
token = 'test_token'
valid = False

#----#
# platform
platform = literal_eval(row['publisher_platforms'])

if len(platform) > 1:
    warnings.warn(f'More than one platform detected at index {index}.')
else:
    platform = platform[0]

# all_fields
all_fields = {k: v for k, v in literal_eval(row.get('all_fields'))}

# targeting
targeting = literal_eval(row.get('targeting'))

# response
response = row.get('response')
if response[0] == "{":
    response = json.loads(row.get('response'))
elif response[0] == '[':
    response = literal_eval(row.get('response'))
elif response[:2] == "b\'":
    response = json.loads(literal_eval(row.get('response')).decode('utf-8'))

# prepare: geo_locations
geo = all_fields['geo_locations']  # literal_eval(row.get('geo_locations'))

# age
ages_ranges = literal_eval(row.get('ages_ranges'))
if isinstance(ages_ranges, dict):
    age_min = ages_ranges.get('min')
    age_max = ages_ranges.get('max')
elif isinstance(ages_ranges, list):
    age_min = ages_ranges[0]
    age_max = ages_ranges[1]

# prepare API arguments
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

# submit API request
url='http://127.0.0.1/api/v1/write'
response = requests.get(url=url, params=args)
response = literal_eval(json.dumps(response.json()))

df.loc[index, 'timestamp_api'] = response.get('timestamp')
df.loc[index, 'status_api'] = int(response.get('status'))
df.loc[index, 'message_api'] = response.get('message')

# ---- API ---- #

# default valid = False
if 'valid' not in args.keys():
    args['valid'] = False

# check arguments
result = check_args(args,
                    required=['token', 'platform', 'timestamp', 'geo_locations', 'gender', 'age_min', 'dau', 'valid'],
                    required_oneof=['mau', 'mau_lower', 'mau_upper'],
                    optional=['valid', 'country', 'collection', 'age_max', 'all_fields', 'targeting', 'response'])
args = result.get('args')
status = result.get('status')
message = result.get('message')

# validate token
args['contributor_id'] = 1
args.pop('token')

# register collection
args['collection_id'] = 999

# reformat timestamp
dt_obj = datetime.datetime.fromtimestamp(int(args.get('timestamp')))
args['collection_date'] = "'" + dt_obj.strftime('%Y-%m-%d') + "'"
# args['timestamp_iso'] = "'" + dt_obj.isoformat(sep=" ")[:-3] + "'"

# table name
table = args.pop('table')

# create sql query
sql = "INSERT INTO " + table + "({}) VALUES({});".format(','.join(args.keys()),
                                                         ','.join([str(i) for i in args.values()]))


