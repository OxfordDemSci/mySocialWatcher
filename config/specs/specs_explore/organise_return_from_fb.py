import time

import pandas as pd
import json
import requests
from config.specs.specs_explore.params import  params_all,url,file_paths
import string
from datetime import datetime


# params zone

params_all = {key: value for key, value in params_all.items() if key not in ['region', 'country', 'city']}

for spec_cat in params_all.keys():
    print(spec_cat)
    json_file_path,csv_file_path= file_paths(spec_cat)

# situation1: directly send request and store the result (return num should be under 1000)

# select the params for specific category, e.g. behaviour, country
    params = params_all[spec_cat]

    response = requests.get(url, params=params)
    specs_json = json.loads(response.text)
    content = specs_json['data']
    df = pd.DataFrame(content)

    # save jason file
    with open(json_file_path, 'w') as f:
        f.write(json.dumps(specs_json,indent=4))

    # save df
    df.to_csv(csv_file_path, index=False)
    time.sleep(1)



# situation 2: city and region
def get_city_or_region(params_all,spec_cat,csv_file_path):
    print(datetime.now())
    df_city = pd.DataFrame()
    #df_city = pd.read_csv(csv_file_path)
    refine_lst = []

    def get_data(q):
        try:
            params = params_all[spec_cat]
            params['q'] = q
            response = requests.get(url, params=params_all[spec_cat])
            specs_json = json.loads(response.text)
            content = specs_json['data']
            df = pd.DataFrame(content)

            if len(df)==1100:
                return "another level"
            else:
                return df
        except:
            print(f'error with {q}, no return')
            return None

    for q in list(string.ascii_lowercase):
        print(q)
        params = params_all[spec_cat]

        re = get_data(q)
        if isinstance(re, pd.DataFrame):
            df=re.copy()
            print(f'for {q},len_df={len(df)}, len df_city = {len(df_city)}')

            df_city = pd.concat([df_city, df], axis=0)
            df_city.drop_duplicates(inplace=True)


        elif isinstance(re, str):
            for q_2 in list(string.ascii_lowercase):
                q_combined_2 = q+q_2


                re = get_data(q_combined_2)
                if isinstance(re, pd.DataFrame):
                    df = re.copy()

                    df_city = pd.concat([df_city, df], axis=0)
                    df_city.drop_duplicates(inplace=True)
                    print(f'for {q_combined_2},len_df={len(df)}, len df_city = {len(df_city)}')
                    df_city.to_csv(csv_file_path)
                elif isinstance(re, str):


                    for q_3 in list(string.ascii_lowercase):
                        q_combined_3 = q_combined_2 + q_3

                        re = get_data(q_combined_3)
                        if isinstance(re, pd.DataFrame):
                            df = re.copy()

                            df_city = pd.concat([df_city, df], axis=0)
                            df_city.drop_duplicates(inplace=True)
                            print(f'for {q_combined_3},len_df={len(df)}, len df_city = {len(df_city)}')
                            df_city.to_csv(csv_file_path)
                        elif isinstance(re, str):
                            refine_lst += q_combined_3
                        else:
                            continue

                else:
                    continue
        else:
            continue

        df_city.to_csv(csv_file_path,index=False)
    print(datetime.now())


get_city_or_region(params_all,spec_cat,csv_file_path)
