import os
import json
import pandas as pd
from mysocialwatcher.specs import multicountry_specs

if __name__ == '__main__':

    # ---- settings ---- #

    # virtual machine name
    vm = 'saffron'

    # collection name
    collection = 'ukraine_countries'

    # ---- credentials ---- #

    # credentials master file
    master_credentials_path = os.path.join('deploy', 'my', 'credentials_master.csv')

    # path for output credentials.csv
    credentials_path = os.path.join('deploy', 'docker', vm, collection, 'credentials.csv')

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
                 'AT', 'LV', 'SE', 'BE', 'HR', 'DK', 'FI', 'IS', 'IE', 'LI', 'LT','LU', 'MT', 'NL', 'NO', 'SI', 'CH',
                 'US']

    # output directory
    out_dir = os.path.join('deploy', 'docker', vm, collection, 'specs')
    os.makedirs(out_dir, exist_ok=True)

    # cleanup old specs
    for f in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, f))

    specs_template = multicountry_specs(countries=countries, name='ukraine_countries')

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
            file_out = os.path.join(out_dir, 'specs' + str(i_count) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))
