import os
import shutil
import json
import pandas as pd

# virtual machine and collection names
vm = 'saffron'
collection = 'ukraine_europe'


if __name__ == '__main__':

    # ---- paths ---- #
    master_credentials_path = os.path.join('config', 'private', 'credentials_master.csv')
    specs_template_path = os.path.join('config', 'specs', 'templates')
    out_dir = os.path.join('docker', 'collectors', vm, collection)
    os.makedirs(out_dir, exist_ok=True)

    # ---- credentials ---- #

    # path for output credentials.csv
    credentials_path = os.path.join(out_dir, 'credentials.csv')

    # load master credentials
    master_credentials = pd.read_csv(master_credentials_path)

    # filter vm and collection
    credentials = master_credentials.loc[(master_credentials.vm == vm) &
                                         (master_credentials.collection == collection)]

    # save to csv
    credentials.to_csv(credentials_path,
                       columns=['token', 'app'],
                       header=False,
                       index=False)

    # ---- collection specs ---- #

    # countries
    countries = ['IT', 'CZ', 'DE', 'ES', 'PT', 'FR', 'GR', 'GB', 'BG', 'EE', 'AT', 'LV', 'SE', 'BE', 'HR',
                 'DK', 'FI', 'IS', 'IE', 'LI', 'LT','LU', 'MT', 'NL', 'NO', 'SI', 'CH', 'US', 'GE']

    # output directory
    specs_dir = os.path.join(out_dir, 'specs')
    os.makedirs(specs_dir, exist_ok=True)

    # cleanup old specs
    for f in os.listdir(specs_dir):
        os.remove(os.path.join(specs_dir, f))

    i_count = 0
    for country in countries:

        # specs template json
        country_specs_template_path = os.path.join(specs_template_path, country + '_regions.json')

        # template json
        with open(country_specs_template_path) as f:
            specs = json.load(f)
        specs['name'] = collection

        # 10-year age classes
        specs['ages_ranges'] = [[13, None], [18, None], [20, None], [60, None], [65, None],
                                [13, 19], [15, 49], [15, 64], [20, 59], [18, 60],
                                [20, 29], [30, 39], [40, 49], [50, 59]]

        # location types
        for i in range(len(specs['geo_locations'])):
            specs['geo_locations'][i]['location_types'] = ['recent', 'home']

        # ---- All languages ----#
        i_count += 1

        specs['languages'] = [None]

        file_out = os.path.join(specs_dir, 'specs' + str(i_count).zfill(3) + '.json')
        with open(file_out, "w") as f:
            f.write(json.dumps(specs))

        # ---- Ukrainian language ----#
        i_count += 1

        specs['languages'] = [{'name': 'Ukrainian', 'values': [52]}]

        file_out = os.path.join(specs_dir, 'specs' + str(i_count).zfill(3) + '.json')
        with open(file_out, "w") as f:
            f.write(json.dumps(specs))

        # ---- Russian language ---- #
        i_count += 1

        specs['languages'] = [{'name': 'Russian', 'values': [17]}]

        file_out = os.path.join(specs_dir, 'specs' + str(i_count).zfill(3) + '.json')
        with open(file_out, "w") as f:
            f.write(json.dumps(specs))
