import numpy as np
from src import params
from datetime import datetime
import pandas as pd

# deal with the fb keys and vk keys

# keys = pd.read_csv(params.work_path/'useful_files'/'dat_regions_keep_key.csv')
keys = pd.read_csv(params.work_path/'useful_files'/'dat_cities_keep.csv',index_col=0)

# country_dict = {'UA':'Ukraine', 'PL':'Poland', 'RU':'Russia', 'BY':'Belarus', 'RO':'Romania', 'SK':'Slovakia', 'HU':'Hungry', 'MD':'Moldova'}
country_dict = {'Ukraine':'UA', 'Poland':'PL', 'Russia':'RU', 'Belarus':'BY', 'Romania':'RO', 'Slovakia':'SK', 'Hungry':'HU', 'Moldova':'MD'}

city_dict = params.city_dict

df = pd.DataFrame(columns=['country','country_code','city_vk','city_fb','fb_key','VK_key','region_id'])
for country in city_dict.keys():
    county_code = country_dict[country]
    for city in city_dict[country].keys():
        df.loc[len(df)] = {'country':country,'country_code':county_code,'city_vk':city,'city_fb':None,'fb_key':None,'VK_key':city_dict[country][city],'region_id':None}

# loop over cities
for county_code in country_dict.values():
    print(county_code)

    cities_in_fb = keys[keys['country_code'] == county_code]['name']
    cities_in_vk = df[df['country_code'] == county_code]['city_vk']

    for city_in_vk in cities_in_vk:

        print("--------------------------------------------------------")
        print(city_in_vk)
        print("--------------------------------------------------------")
        count = 0
        multi_city_dict = {}

        # Russia,RU,Moscow,Moscow,2020916,1,3146
        # RU,Samara,Samara,2057702,123,3164
        for city_in_fb in cities_in_fb:

            if city_in_vk in city_in_fb:
                if city_in_vk == city_in_fb:
                    print('find unique value')

                    fb_key = keys[keys['name'] == city_in_fb]['key'].values[0]
                    region_id = keys[keys['name'] == city_in_fb]['region_id'].values[0]
                    print('city is {} in vk and {} in fb, fb_key is {}, region_id is {}'.format( city_in_vk,
                                                                                                city_in_fb, fb_key,
                                                                                                region_id))

                    df.loc[df['city_vk'] == city_in_vk, 'city_fb'] = city_in_fb
                    df.loc[df['city_vk'] == city_in_vk, 'fb_key'] = fb_key
                    df.loc[df['city_vk'] == city_in_vk, 'region_id'] = region_id
                    switch = 1  # unique/identical value found
                    break
                else:
                    switch = 2  # need to make choices
                    fb_key = keys[keys['name'] == city_in_fb]['key'].values[0]
                    region_id = keys[keys['name'] == city_in_fb]['region_id'].values[0]

                    multi_city_dict[str(count)] = [city_in_fb, fb_key,region_id]
                    print('choice[{}]:city is {} in vk and {} in fb, fb_key is {}, region_id is {}'.format(count,city_in_vk,city_in_fb,fb_key,region_id))
                    count += 1

            else:
                if len(multi_city_dict) == 0:
                    switch = 3  # no matched value found
                    # print('for city {} there is no matched value found'.format(city_in_fb))
                else:
                    switch = 2  # still need to make decision

        if switch == 2:
            print("--------------------------------------------------------")
            choice = input("select the one you find most proper,-1 is no matched value, r is only region_id found")
            if choice == '-1':
                # no matched value
                continue
            elif choice == 'r':
                # find region key
                choice = input("select the one you find most proper")
                df.loc[df['city_vk'] == city_in_vk,'city_fb'] = multi_city_dict[choice][0]
                df.loc[df['city_vk'] == city_in_vk, 'fb_key'] = None
                df.loc[df['city_vk'] == city_in_vk, 'region_id'] = multi_city_dict[choice][2]
            else:
                df.loc[df['city_vk'] == city_in_vk, 'city_fb'] = multi_city_dict[choice][0]
                df.loc[df['city_vk'] == city_in_vk, 'fb_key'] = multi_city_dict[choice][1]
                df.loc[df['city_vk'] == city_in_vk, 'region_id'] = multi_city_dict[choice][2]

        elif switch ==3:
            #choice = input('input 0 if you want to leave it blank, 1 if you want to')
            continue


# manual zone
# df_none = df[df['fb_key'].isna()]

# df.to_csv(params.specify_path/'vk_fb_city_key_matched.csv')
# df_none.to_csv(params.specify_path/'vk_fb_city_key_non_matched.csv')


# now we check the keys


# df is generated above
'''
df = pd.read_csv(params.specify_path/'vk_fb_city_key_matched.csv',index_col=0)
city_not_in_fb_key = df.loc[df['fb_key'].isna(),'city_vk'].values
city_not_in_region_key = df.loc[df['region_id'].isna(),'city_vk'].values

'''
