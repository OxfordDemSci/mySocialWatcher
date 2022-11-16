import os
import shutil
import json
import pandas as pd
import sys
sys.path.append(os.getcwd())
from mysocialwatcher.collector.specs import multicountry_specs

# virtual machine and collection names
vm = 'saffron'
collection = 'ukraine_countries'


if __name__ == '__main__':

    # ---- paths ---- #
    master_credentials_path = os.path.join('config', 'private', 'credentials_master.csv')
    specs_template_path = None
    env_template_path = os.path.join('config', 'private', 'collector.env')
    out_dir = os.path.join('docker', 'collectors', vm, collection)
    os.makedirs(out_dir, exist_ok=True)

    # ---- environment ---- #
    shutil.copy(src=env_template_path,
                dst=os.path.join(out_dir, '.env'))

    env_lines = ['FREQUENCY=7']
    with open(os.path.join(out_dir, '.env'), 'a') as f:
        f.writelines(env_lines)

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
    countries = ['UA', 'MD', 'RO', 'PL', 'HU', 'SK', 'BY', 'IT', 'CZ', 'DE', 'ES', 'PT', 'FR', 'GR', 'GB', 'BG', 'EE',
                 'AT', 'LV', 'SE', 'BE', 'HR', 'DK', 'FI', 'IS', 'IE', 'LI', 'LT', 'LU', 'MT', 'NL', 'NO', 'SI', 'CH',
                 'US']

    # output directory
    specs_dir = os.path.join(out_dir, 'specs')
    os.makedirs(specs_dir, exist_ok=True)

    # cleanup old specs
    for f in os.listdir(specs_dir):
        os.remove(os.path.join(specs_dir, f))

    specs_template = multicountry_specs(countries=countries, name='ukraine_countries')
    specs_template['name'] = collection

    languages = [None,
                 {'name': 'Ukrainian', 'values': [52]},
                 {'name': 'Russian', 'values': [17]}]

    location_types = ['recent',
                      'home',
                      'travel_in',
                      ['home', 'recent']]

    i_count = 0
    for location_type in location_types:
        for language in languages:

            i_count += 1

            specs = specs_template

            # language
            specs['languages'] = [language]

            # location types
            for i in range(len(specs['geo_locations'])):
                specs['geo_locations'][i]['location_types'] = [location_type]

            # save json
            file_out = os.path.join(specs_dir, 'specs' + str(i_count).zfill(3) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))
