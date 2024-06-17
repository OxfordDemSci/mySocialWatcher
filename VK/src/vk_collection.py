import random
from src import upload
import requests
import re
from src import params
import pandas as pd
import time
import datetime
import numpy as np
import sys
import os
import logging
from src import collection_components
def get_audience(url, headers, data, df, index):
    res = requests.post(url, headers=headers, data=data)
    x = res.text
    try:
        audience = re.findall('\"audience_count\":(\d*),', x)[0]
    except:
        # audience = None
        print('error here in row {}'.format(index))
        logging.error('collector stopped at {}'.format(index))
        today = str(datetime.datetime.now().strftime('%y%m%d')) + '.csv'
        df.to_csv(params.data_path / today, index=False)
        sys.exit(1)
    print(audience)
    time.sleep(random.randint(8, 10))
    return audience
def get_collection_specs_dict(row):
    collection_specs_dict = {'age_group': [row['age_min'], row['age_max']],
                             'gender_code': params.gender_dict[row['gender']],
                             'country_code': params.country_dict[row['country']]}
    if pd.isna(row['city']):
        pass
    else:
        collection_specs_dict['city_code'] = params.city_dict[row['country']][row['city']]
    return collection_specs_dict
# executing process starts here
# creat logs
logging.basicConfig(filename=params.specify_path / 'collection_logs.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR)
today = str(datetime.datetime.now().strftime('%y%m%d')) + '.csv'
headers = collection_components.update_cookie()
if os.path.exists(params.data_path/today):
    df = pd.read_csv(params.data_path/today)
    df1=pd.read_csv(params.specify_path/params.schedule_filename)
    df['country_level']=df1['country_level']
else:
    df = pd.read_csv(params.specify_path / params.schedule_filename)
for index, row in df.iterrows():
    if pd.isna(row['audience']):
        print(index)
        # country level collection
        if row['country_level'] == 1:
            collection_specs_dict = get_collection_specs_dict(row)
            data = collection_components.data_dict_country_level(age_range=collection_specs_dict['age_group'],
                                                                 gender=collection_specs_dict['gender_code'],
                                                                 country=collection_specs_dict['country_code'])
            audience = get_audience(url=collection_components.url, headers=headers, data=data, df=df, index=index)
            now = datetime.datetime.now()
            df.loc[index, 'audience'] = audience
            df.loc[index, 'time'] = str(now)
        else:
            collection_specs_dict = get_collection_specs_dict(row)
            data = collection_components.data_dict(age_range=collection_specs_dict['age_group'],
                                                   gender=collection_specs_dict['gender_code'],
                                                   country=collection_specs_dict['country_code'],
                                                   city=collection_specs_dict['city_code'],
                                                   traveller=0)
            audience = get_audience(url=collection_components.url, headers=headers, data=data, df=df, index=index)
            now = datetime.datetime.now()
            df.loc[index, 'audience'] = audience
            df.loc[index, 'time'] = str(now)
        df.to_csv(params.data_path/today, index=False)
        print('finished row {}/{}'.format(index, len(df)))
    else:
        continue


upload.upload([today])

