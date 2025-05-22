import os
import json
import pandas as pd
import shutil
import numpy as np

# virtual machine and collection names
vm = 'saffron'
collection = 'ukraine_regions_homerecent'


if __name__ == '__main__':

    # ---- paths ---- #
    master_credentials_path = os.path.join('config', 'private', 'credentials_master.csv')
    specs_template_path = os.path.join('config', 'specs', 'templates', 'UA_regions.json')
    out_dir = os.path.join('docker', 'collectors', vm, collection)
    os.makedirs(out_dir, exist_ok=True)
    yagmail_path = os.path.join('config', 'private', 'yagmail.csv')

    # ---- yagmail credential ---- #
    if os.path.exists(yagmail_path):
        shutil.copy2(yagmail_path, os.path.join(out_dir, 'yagmail.csv'))

    # ---- credentials ---- #

    # path for output credentials.csv
    credentials_path = os.path.join(out_dir, 'credentials.csv')

    # load master credentials
    master_credentials = pd.read_csv(master_credentials_path)

    # filter vm and collection
    credentials = master_credentials.loc[(master_credentials.vm == vm) &
                                         (master_credentials.collection == collection)]

    # convert app to int
    credentials = credentials.copy()
    credentials['app'] = credentials['app'].astype(np.int64)

    # save to csv
    credentials.to_csv(credentials_path,
                       columns=['token', 'app'],
                       header=False,
                       index=False)

    # ---- collection specs ---- #

    # output directory
    specs_dir = os.path.join(out_dir, 'specs')
    os.makedirs(specs_dir, exist_ok=True)

    # cleanup old specs
    for f in os.listdir(specs_dir):
        os.remove(os.path.join(specs_dir, f))

    # template json
    with open(specs_template_path) as f:
        specs = json.load(f)
    specs['name'] = collection

    # location types
    for i in range(len(specs['geo_locations'])):
        if 'location_types' in specs['geo_locations'][i].keys():
            del specs['geo_locations'][i]['location_types']

    # ---- All languages ----#

    # facebook
    specs["publisher_platforms"] = ['facebook']
    specs['languages'] = [None]

    file_out = os.path.join(specs_dir, '1_facebook_all.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))

    # instagram
    specs["publisher_platforms"] = ['instagram']
    specs['languages'] = [None]

    file_out = os.path.join(specs_dir, '2_instagram_all.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))

    # ---- Ukrainian language ----#

    # facebook
    specs["publisher_platforms"] = ['facebook']
    specs['languages'] = [{'name': 'Ukrainian', 'values': [52]}]

    file_out = os.path.join(specs_dir, '3_facebook_ukrainian.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))

    # instagram
    specs["publisher_platforms"] = ['instagram']
    specs['languages'] = [{'name': 'Ukrainian', 'values': [52]}]

    file_out = os.path.join(specs_dir, '4_instagram_ukrainian.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))

    # ---- Russian language ---- #

    # facebook
    specs["publisher_platforms"] = ['facebook']
    specs['languages'] = [{'name': 'Russian', 'values': [17]}]

    file_out = os.path.join(specs_dir, '5_facebook_russian.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))

    # instagram
    specs["publisher_platforms"] = ['instagram']
    specs['languages'] = [{'name': 'Russian', 'values': [17]}]

    file_out = os.path.join(specs_dir, '6_instagram_russian.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))

