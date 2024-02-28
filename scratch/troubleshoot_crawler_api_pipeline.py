import pandas as pd
from ast import literal_eval
import json
import warnings
import math
import datetime
import requests
import numpy
from mysocialwatcher.api.utils import check_args
from mysocialwatcher.api import app, endpoints
from mysocialwatcher.api.utils import *
from dotenv import load_dotenv

load_dotenv('docker/datahub/.env')



# load problem data
file = '/research/git/OxfordDemSci/mySocialWatcher/data/test/test/finished/dataframe_collected_finished_MU_country_and_gadm1_part_1_20240224_betterestimate.csv'
df = pd.read_csv(file)

# ---- SIMULATION ----#

index_success = []
length_success = []
index_fail = []
length_fail = []
for index in range(df.shape[0]):

    # select problem row
    # index = 15  # 15, 31, 35, 51, 55, 71, 75, 91, 94, 95, 115, 131, 135, 151, 152, 154, 155, 171, 175, 191, 195, 215, 231, 235, 251, 252, 254, 255, 271, 275, 291, 295
    print('Index: ' + str(index))

    row = df.iloc[index]

    # -- CRAWLER --#

    # arguments
    collection_name = 'test_collection'
    token = '439b2ef701440dcf519b853a890240b6'
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
    # response = requests.get(url=url, params=args)

    # prepare data
    for arg in args.keys():
        if isinstance(args.get(arg), numpy.int64):
            args[arg] = int(args.get(arg))

    # data_bytes = json.dumps(args).encode('utf-8')
    # data_json = json.dumps(args)

    #-- headers --#
    # headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'}
    # headers={'Content-Encoding': 'gzip'}
    # headers={'Transfer-Encoding': 'chunked'}
    # headers = {'content-type': "application/json", 'cache-control': "no-cache"}

    try:
        http_response_dict = http_response = request_prep = request = None
        s = requests.Session()

        request = requests.Request('POST', url, json=args)
        request_prep = request.prepare()
        request_prep.headers
        http_response = s.send(request_prep)

        if http_response.status_code in [200, 409]:
            index_success.append(index)
            length_success.append(int(request_prep.headers.get('Content-Length')))
            print('    status: ' + str(http_response.status_code))
        else:
            index_fail.append(index)
            length_fail.append(int(request_prep.headers.get('Content-Length')))
            print('    status: ' + str(http_response.status_code))
            print('    response: ' + http_response.text)

    except Exception as e:
        print('    exception: ' + str(e))
        index_fail.append(index)
        length_fail.append(int(request_prep.headers.get('Content-Length')))

print('Success min length: ' + str(min(length_success)))
print('Success max length: ' + str(max(length_success)))
print('Fail min length: ' + str(min(length_fail)))
print('Fail max length: ' + str(max(length_fail)))












###################################################################

http_response_dict = json.loads(json.dumps(http_response.json()))

df.loc[index, 'timestamp_api'] = http_response_dict.get('timestamp')
df.loc[index, 'status_api'] = int(http_response_dict.get('status'))
df.loc[index, 'message_api'] = http_response_dict.get('message')

# ---- API ---- #

if request.method == 'GET':
    args = dict(request.args)
elif request.method == 'POST':
    args = request.json


#-- check_args --#

# default valid = False
if 'valid' not in args.keys():
    args['valid'] = False

# check arguments
result = check_args(args,
                    required=['token', 'platform', 'timestamp', 'geo_locations', 'gender', 'age_min', 'dau', 'valid'],
                    required_oneof=['mau', 'mau_lower', 'mau_upper'],
                    optional=['valid', 'country', 'collection', 'age_max', 'all_fields', 'targeting', 'response'])
args = result.get('args')


#-- write endpoint --#
db = db_engine(host='127.0.0.1')

# validate token
result = validate_token(token=args.get('token'), conn=db.connect(), write_access=True)
status = result.get('status')
if status == 200:
    args['contributor_id'] = result.get('contributor_id')
    args.pop('token')
else:
    message = result.get('message')

# process request
if status == 200:

    # collection id
    if 'collection' in args.keys():

        collection_id = register_collection(collection_name=args.pop('collection'),
                                            conn=db.connect())

        if isinstance(collection_id, int):
            args['collection_id'] = collection_id

# reformat timestamp
dt_obj = datetime.datetime.fromtimestamp(int(args.get('timestamp')))
args['collection_date'] = "'" + dt_obj.strftime('%Y-%m-%d') + "'"
# args['timestamp_iso'] = "'" + dt_obj.isoformat(sep=" ")[:-3] + "'"

# table name
table = args.pop('table')

# create sql query
sql = "INSERT INTO " + table + "({}) VALUES({});".format(','.join(args.keys()),
                                                         ','.join([str(i) for i in args.values()]))


with db.connect() as conn:
    result = conn.execute(sql)