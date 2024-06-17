import requests
import re
from src import params
import pandas as pd
import time
import datetime
import numpy as np


'''
# The schedule
# There are 100 cities in 8 countries 
#--------------------------------------------------------------------------------------------------
# 1. At the country level: 
#       for gender type = 0 (all), we collect 18+ age group (count: 8)
#       for gender type = 1 or 2, we collect data for 10 age groups (count: 8*2*10=160)
#--------------------------------------------------------------------------------------------------
# 2. At city level:
#       for gender type = 0 (all), we collect only 18+ group (count: 100)
#       for gender type = 1 or 2, we collect data for 10 age groups (count: 100*2*10=2000)
#--------------------------------------------------------------------------------------------------
# we have 2268 records in total 
#--------------------------------------------------------------------------------------------------

for country Ukraine, there are 15 cities
for country Poland, there are 12 cities
for country Russia, there are 21 cities
for country Belarus, there are 12 cities
for country Romania, there are 11 cities
for country Slovakia, there are 9 cities
for country Hungry, there are 11 cities
for country Moldova, there are 9 cities

'''
country_dict_to_iterate = params.country_dict
gender_dict = params.gender_dict
age_lst = params.age_lst
audience,now = None,None



# here we generate the city_keys
def keys_generator():
    fb_keys = pd.read_csv(params.specify_path/'vk_fb_city_key_matched.csv',index_col=0)
    city_keys={}
    fb_key_count=[]
    region_count = []
    for index, row in fb_keys.iterrows():
        try:
            fb_key = row['fb_key']
            region_id = row['region_id']
            city_keys[row['city_vk']] = {'fb_key': None if np.isnan(fb_key) else int(fb_key),
                                         'region_id':None if np.isnan(region_id) else int(region_id),
                                         'vk_key': row['VK_key']}
            if np.isnan(fb_key):
                fb_key_count.append(row['city_vk'])
            if (np.isnan(region_id)):
                region_count.append(row['city_vk'])

        except:
            print("error in city {}".format(row['city_vk']))
    return city_keys


keys = keys_generator()

# keys = params.keys
# = params.country_dict
df = pd.DataFrame(columns=['country','city','age_min','age_max','age_group','gender','audience','time','country_level', 'fb_key','vk_key','region_id'])

for country_name, country_code in country_dict_to_iterate.items():
    # store the data at the country level
    for gender_name, gender_code in gender_dict.items():
        country_level = 1
        if gender_name == 'all':
            # only scrape 18+ for gender == all
            country_level = 1
            age_group = {"min":18,"max":0}
            age_range = 1899
            df = df.append({'time': now, 'country': country_name, 'city': None, 'age_min': age_group["min"],
                            'age_max': age_group["max"], 'age_group': age_group["min"] * 100 + age_group["max"],
                            'gender': gender_name, 'audience': audience, 'country_level': country_level,
                            'fb_key':None, 'region_id':None, 'vk_key':country_code}, ignore_index=True)
            # print(len(df))
        else:
            # rest genders
            for age_group in age_lst:
                country_level = 1
                age_range = age_group["min"] * 100 + (99 if age_group["max"] == 0 else age_group["max"])
                df = df.append({'time': now, 'country': country_name, 'city': None, 'age_min': age_group["min"],
                                'age_max': age_group["max"], 'age_group': age_group["min"] * 100 + age_group["max"],
                                'gender': gender_name, 'audience': audience, 'country_level': country_level,
                                'fb_key':None,'region_id':None, 'vk_key':country_code},ignore_index=True)
    # store the data at city level
    city_count = 0
    city_dict = params.city_dict[country_name]
    for city_name, city_code in city_dict.items():
        city_count+=1
        country_level=0
        # print('City Level: deal for city {} ({}/{}) in {}'.format(city_name, city_count,len(city_dict),country_name ))
        for gender_name, gender_code in gender_dict.items():

            # situation of gender == all, only age group 18-99 is collected
            if gender_name == 'all':
                age_group = {"min":18,"max":0}
                age_range = 1899
                if city_code == keys[city_name]['vk_key']:
                    df = df.append({'time': now, 'country': country_name, 'city': city_name, 'age_min': age_group["min"],
                                    'age_max': age_group["max"], 'age_group': age_group["min"] * 100 + age_group["max"],
                                    'gender': gender_name, 'audience': audience,'country_level':country_level,
                                    'fb_key':keys[city_name]['fb_key'],'vk_key':city_code, 'region_id': keys[city_name]['region_id']}, ignore_index=True)
                    # print(len(df))
                else:
                    print('error')
            else:
                for age_group in age_lst:

                    age_range = age_group["min"]*100 + (99 if age_group["max"]==0 else age_group["max"])
                    if city_code == keys[city_name]['vk_key']:
                        df = df.append({'time': now,'country': country_name,'city':city_name,'age_min':age_group["min"],
                                        'age_max': age_group["max"],'age_group':age_group["min"]*100+age_group["max"],
                                        'gender': gender_name,'audience':audience,'country_level':country_level,
                                        'fb_key': keys[city_name]['fb_key'],'vk_key':city_code, 'region_id': keys[city_name]['region_id']},ignore_index=True)
                        # print(len(df))
                    else:
                        print('error 2')
df = df.rename(columns={'age_group': 'age_range'})

# df.to_csv(params.specify_path/params.schedule_filename,index=False)
#

# set(df.loc[(df['region_id'].isna()) &(df['country_level']==0)]['city'])

df = pd.read_csv(params.specify_path/params.schedule_filename)
fb_keys = pd.read_csv(params.work_path/'useful_files/dat_cities_keep.csv',index_col=0)
vk_keys = params.city_dict
all_keys = params.keys
cities = list(set(df['city']))
match = pd.read_csv(params.specify_path/'vk_fb_city_key_matched.csv',index_col=0)

cities.remove('Simferopol')
cities.remove(np.nan)
# we first check the schedule file


for city in cities:
    print('check schedule for city {}, {}/{}'.format(city,cities.index(city),len(cities)))
    rows = df[df['city']==city].reset_index(drop=True)
    if (len(rows['fb_key'].unique())==1) & (len(rows['vk_key'].unique())==1) & (len(rows['region_id'].unique())==1):
        # print('pass check 1: the unique number of fb_key,vk_key and region_id =1')
        row = rows.iloc[0,]
        country, city = row['country'], row['city']
        fb_key_to_check,vk_key_to_check,region_id_to_check = row['fb_key'],row['vk_key'],row['region_id']

        fb_city_name = match.loc[match['city_vk']==city,'city_fb'].values[0]
        fb_key = fb_keys.loc[fb_keys['name']==fb_city_name,'key'].values[0]
        region_id = fb_keys.loc[fb_keys['name']==fb_city_name,'region_id'].values[0]
        vk_key = vk_keys[country][city]

        if (fb_key_to_check==fb_key) & (vk_key==vk_key_to_check)&(region_id_to_check==region_id):
            continue
            # print('pass check 2 : all the same')
        else:
            print('error 02')
        #print('country :{}, city : {} fb_key is {}/{}, vk_key is {}/{}, region id is {}/{}'.format(country,city,fb_key,fb_key_to_check,vk_key_to_check,vk_key,region_id_to_check,region_id) )
    else:
        error = 1
        print('error 01 ')
        print(rows['fb_key'].unique())
        print(rows['vk_key'].unique())
        print(rows['region_id'].unique())
        break

