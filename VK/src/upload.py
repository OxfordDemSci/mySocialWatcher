import datetime
from src import params
import pandas as pd
import numpy as np
import requests
import os


def post_process_before_upload(df):
    # 1.time stamps
    df.loc[df['time'].isna(), 'time'] = None
    df['time_stamp'] = [x if x == None else datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f").timestamp() for x in
                        df['time']]
    # country
    country_dict = {'Ukraine': 'UA', 'Poland': 'PL', 'Russia': 'RU', 'Belarus': 'BY', 'Romania': 'RO', 'Slovakia': 'SK',

                    'Hungry': 'HU', 'Moldova': 'MD'}
    df['country_code'] = df['country'].replace(country_dict)
    df['city'] = df['city'].replace(np.nan, 'not_city')

    # gender
    gender_dict = {"male": 1, "female": 2, "all": 0}
    df['gender'] = df['gender'].replace(gender_dict)

    return df


# for all files 


def upload(files):
    region_name_dict = params.region_dict

    count = 0
    for file in files:

        count += 1

        df = pd.read_csv(params.data_path/file)
        # post process
        df = post_process_before_upload(df)

        # delete city Simferopol for now

        df = df[df['city']!="Simferopol"]
        stop_sign = False

        for index, row in df.iterrows():

            if row['time'] != None:
                time_stamp = row['time_stamp']
                country_code = row['country_code']
                gender = row['gender']
                estimate = row['audience']
                fb_key = row['fb_key']
                vk_key = row['vk_key']
                region_id = row['region_id']
                city_name = row['city']
                if city_name == 'not_city':
                    # country level
                    geo_locations = {"name": "countries",
                                     "values": [country_code],
                                     "location_types": ["home"]}
                else:
                    # city level
                    # print('fb_key is {}({}), vk_key is {}({})'.format(fb_key,type(fb_key),vk_key,type(vk_key)))
                    geo_locations = {"name": "cities",
                                     "values": [{"key": fb_key if np.isnan(fb_key) else int(fb_key),
                                                 "name": city_name,
                                                 "region_id": region_id if np.isnan(region_id) else int(region_id),
                                                 "region": None if np.isnan(region_id) else region_name_dict[int(region_id)] ,
                                                 "vk_key": int(vk_key),
                                                 "country_code": country_code}],
                                     "location_types": ["home"]}

                geo_locations = str(geo_locations).replace("'", '"')

                age_min = row['age_min']
                age_max = 999 if row['age_max'] == 0 else row['age_max']
                args = {
                    "token": "7892291fe7f462be2027c386251f0c23",
                    "valid": "True",
                    "platform": "vkontakte",
                    "timestamp": int(time_stamp),
                    "country": country_code,
                    "gender": int(gender),
                    "dau": int(estimate),
                    "mau_lower": None,
                    "mau_upper": None,
                    "geo_locations": geo_locations,
                    "age_min": age_min,
                    "age_max": age_max}

                print('deal for file {}, {}/{}; record {}/{} within the file'.format(file, count, len(files),index+1,len(df)))
                # print(args)
                response = requests.get(url='http://10.131.129.27/api/v1/social_media_audience/write', params=args)
                # print(response.text)
                if "OK" in response.text:
                    continue
                elif "Bad" in response.text:
                    print(response.text)
                    print(args)
                    stop_sign = True
                    break

                else:
                    print(response.text)
            else:
                print('error here!')
        if stop_sign:
            break
        else:
            # stop_sign = False
            continue


# upload(['260322.csv','270322.csv'])
'''
# list files
# files=[str(datetime.datetime.now().strftime('%d%m%y')) + '.csv']
files = os.listdir(params.data_path)
files.remove('.DS_Store')

df1 = pd.read_csv(params.specify_path / params.schedule_filename)
'''
'''
# add the fb_key to all files
df1 = pd.read_csv(params.specify_path/params.schedule_filename)

for file in files:

    df = pd.read_csv(params.data_path/file)
    df['fb_key'] = df1['fb_key']
    df['vk_key'] = df1['vk_key']
    df['region_id'] = df1['region_id']
    df['city'] =df1['city']
    city_fb_nan = set(df[(df['fb_key'].isna()) & (df['country_level']==0)]['city'])
    print('for file {}, city_fb_key is nan is {}'.format(file,city_fb_nan))
    df.to_csv(params.data_path/file,index=False)

keys=pd.read_csv(params.work_path/'useful_files/dat_cities_keep.csv',index_col=0)

region_name_dict = {key:name for key,name in zip(keys['region_id'],keys['region'])}

temp = pd.read_csv(params.data_path/'230322.csv')
temp[(temp['fb_key'].isna()) & (temp['country_level']==0)]


temp[temp['city']=='Samara']
df = temp
'''

