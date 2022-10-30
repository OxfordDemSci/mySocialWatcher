import os
import json
import pandas as pd

if __name__ == '__main__':

    # ---- settings ---- #

    # virtual machine name
    vm = 'niska'

    # collection name
    collection = 'rus_exodus_instagram'

    # credentials master file
    master_credentials_path = os.path.join('deploy', 'my', 'credentials_master.csv')

    # ---- credentials ---- #

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
    countries = ['AE', 'AM', 'AZ', 'CY', 'DE', 'EE', 'EG', 'FI', 'FR', 'GE', 'IL', 'KG', 'KZ', 'LT', 'LV', 'ME', 'PL',
                 'RS', 'TH', 'TJ', 'TR', 'UZ']

    # output directory
    out_dir = os.path.join('deploy', 'docker', vm, collection, 'specs')
    os.makedirs(out_dir, exist_ok=True)

    # cleanup old specs
    for f in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, f))

    i_count = 0
    for country in countries:
        for platform in ['instagram']:

            # specs template json
            specs_template_path = os.path.join('deploy', 'specs', 'templates', country + '_regions.json')

            # template json
            with open(specs_template_path) as f:
                specs = json.load(f)

            # location types
            for i in range(len(specs['geo_locations'])):
                specs['geo_locations'][i]['location_types'] = ['recent', 'home']

            # platform
            specs["publisher_platforms"] = [platform]

            # ---- All languages ---- #
            i_count += 1

            specs['languages'] = [None]

            file_out = os.path.join(out_dir, 'specs' + str(i_count) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))

            # ---- Russian language ---- #
            i_count += 1

            specs['languages'] = [{'name': 'Russian', 'values': [17]}]

            file_out = os.path.join(out_dir, 'specs' + str(i_count) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))
