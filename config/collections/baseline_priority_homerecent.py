import os
import json
import pandas as pd
import shutil
import numpy as np


# virtual machine and collection names
vm = 'jubal'
collection = 'baseline_priority_homerecent'


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

    # priority country list
    countries = ['AF', 'BD', 'BF', 'BR', 'CD', 'CF', 'CM', 'CO', 'CU', 'DJ', 'EC', 'EG', 'ER', 'ET', 'GH', 'GN', 'GT',
                 'HT', 'IL', 'IQ' ,'IN', 'IR', 'JO', 'LB', 'LY', 'ML', 'MM', 'MZ', 'NE', 'NG', 'NP', 'PE', 'PK', 'PS',
                 'SD', 'SL', 'SO', 'SS', 'SY', 'TD', 'UA', 'VE', 'YE', 'ZA', 'ZM']
    countries.sort()

    # # drop countries from other collections
    # drop_countries = drop_countries + ['CD', 'CF', 'DJ', 'EG', 'ER', 'ET', 'LY', 'SD', 'SS', 'TD']  # see collection: sudan_conflict
    # drop_countries = drop_countries + ['IL', 'PS', 'EG', 'JO', 'LB'] # see collection: israeli_conflict

    # drop countries that will return errors
    drop_countries = ['CU', 'SD', 'IR', 'SY']
    countries = [i for i in countries if i not in drop_countries]

    platforms = ['facebook', 'instagram']

    i = 0
    for country in countries:
        for platform in platforms:
            i += 1

            specs_file = os.path.join(specs_template_path, country + '_regions.json')
            if not os.path.exists(specs_file):
                print('Specs template does not exist: ' + specs_file)
                continue

            # template json
            with open(specs_file) as f:
                specs = json.load(f)
            specs['name'] = collection

            # location types
            for i in range(len(specs['geo_locations'])):
                if 'location_types' in specs['geo_locations'][i].keys():
                    del specs['geo_locations'][i]['location_types']

            # platform
            specs["publisher_platforms"] = [platform]

            # all languages
            specs['languages'] = [None]

            # age groups
            specs['ages_ranges'] = [{"min": 13},
                                    {"min": 15},
                                    {"min": 18},
                                    {"min": 20},
                                    {"min": 50},
                                    {"min": 60},
                                    {"min": 65},
                                    {"min": 13, "max": 19},
                                    {"min": 13, "max": 17},
                                    {"min": 15, "max": 24},
                                    {"min": 15, "max": 49},
                                    {"min": 15, "max": 59},
                                    {"min": 15, "max": 64},
                                    {"min": 18, "max": 24},
                                    {"min": 18, "max": 49},
                                    {"min": 18, "max": 59},
                                    {"min": 18, "max": 64},
                                    {"min": 20, "max": 49},
                                    {"min": 20, "max": 59},
                                    {"min": 20, "max": 64},
                                    {"min": 25, "max": 59},
                                    {"min": 20, "max": 29},
                                    {"min": 30, "max": 39},
                                    {"min": 40, "max": 49},
                                    {"min": 50, "max": 59},
                                    {"min": 15, "max": 19},
                                    {"min": 20, "max": 24},
                                    {"min": 25, "max": 29},
                                    {"min": 30, "max": 34},
                                    {"min": 35, "max": 39},
                                    {"min": 40, "max": 44},
                                    {"min": 45, "max": 49},
                                    {"min": 50, "max": 54},
                                    {"min": 55, "max": 59},
                                    {"min": 60, "max": 64}]

            file_out = os.path.join(specs_dir, '_'.join([country, platform]) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))

