import os
import shutil
import json
import pandas as pd
import numpy as np

# virtual machine and collection
vm = 'niska'
collection = 'rus_exodus_instagram'


if __name__ == '__main__':

    # ---- paths ---- #
    master_credentials_path = os.path.join('config', 'private', 'credentials_master.csv')
    specs_template_path = os.path.join('config', 'specs', 'templates')
    out_dir = os.path.join('docker', 'collectors', vm, collection)
    os.makedirs(out_dir, exist_ok=True)
    yagmail_path = os.path.join('config', 'private', 'yagmail.csv')

    # ---- yagmail credential ---- #
    if os.path.exists(yagmail_path):
        shutil.copy2(yagmail_path, os.path.join(out_dir, 'yagmail.csv'))

    # ---- credentials ---- #

    # credentials master file
    master_credentials = pd.read_csv(master_credentials_path)

    # filter vm and collection
    credentials = master_credentials.loc[(master_credentials.vm == vm) &
                                         (master_credentials.collection == collection)]

    # convert app to int
    credentials = credentials.copy()
    credentials['app'] = credentials['app'].astype(np.int64)

    # save to csv
    credentials.to_csv(os.path.join(out_dir, 'credentials.csv'),
                       columns=['token', 'app'],
                       header=False,
                       index=False)

    # ---- collection specs ---- #

    # countries
    countries = ['AE', 'AM', 'AZ', 'CY', 'DE', 'EE', 'EG', 'FI', 'FR', 'GE', 'IL', 'KG', 'KZ', 'LT', 'LV', 'ME', 'PL',
                 'RS', 'TH', 'TJ', 'TR', 'UZ']

    # output directory
    specs_dir = os.path.join(out_dir, 'specs')
    os.makedirs(specs_dir, exist_ok=True)

    # cleanup old specs
    for f in os.listdir(specs_dir):
        os.remove(os.path.join(specs_dir, f))

    i_count = 0
    for country in countries:
        for platform in ['instagram']:

            # specs template json
            country_specs_template_path = os.path.join(specs_template_path, country + '_regions.json')

            # template json
            with open(country_specs_template_path) as f:
                specs = json.load(f)
            specs['name'] = collection

            # location types
            for i in range(len(specs['geo_locations'])):
                if 'location_types' in specs['geo_locations'][i].keys():
                    del specs['geo_locations'][i]['location_types']

            # platform
            specs["publisher_platforms"] = [platform]

            # ---- All languages ---- #
            i_count += 1

            specs['languages'] = [None]

            file_out = os.path.join(specs_dir, 'specs' + str(i_count).zfill(3) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))

            # ---- Russian language ---- #
            i_count += 1

            specs['languages'] = [{'name': 'Russian', 'values': [17]}]

            file_out = os.path.join(specs_dir, 'specs' + str(i_count).zfill(3) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))

            # ---- Russian Expats ---- #
            i_count += 1

            specs['languages'] = [None]
            specs['behavior'] = [
                {
                    "or": [6025000815983],
                    "name": "Lived in Russia (Formerly Expats - Russia)"
                }
            ]

            file_out = os.path.join(specs_dir, 'specs' + str(i_count).zfill(3) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))

