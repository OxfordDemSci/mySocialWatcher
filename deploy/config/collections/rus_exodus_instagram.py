import os
import shutil
import json
import pandas as pd

if __name__ == '__main__':

    # ---- settings ---- #

    # virtual machine name
    vm = 'niska'

    # collection name
    collection = 'rus_exodus_instagram'

    # paths
    master_credentials_path = os.path.join('deploy', 'config', 'private', 'credentials_master.csv')
    specs_template_path = os.path.join('deploy', 'config', 'specs', 'templates')
    env_template_path = os.path.join('deploy', 'config', 'private', 'collector.env')
    cron_template_path = os.path.join('deploy', 'config', 'cron', 'daily')
    out_dir = os.path.join('deploy', 'docker', 'virtual_machines', vm, collection)
    os.makedirs(out_dir, exist_ok=True)

    # ---- environment ---- #

    shutil.copy(src=env_template_path,
                dst=os.path.join(out_dir, '.env'))

    # ---- cron ---- #

    shutil.copy(src=cron_template_path,
                dst=os.path.join(out_dir, 'cronjob'))

    # ---- credentials ---- #

    # credentials master file
    master_credentials = pd.read_csv(master_credentials_path)

    # filter vm and collection
    credentials = master_credentials.loc[(master_credentials.vm == vm) &
                                         (master_credentials.collection == collection)]

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

            # location types
            for i in range(len(specs['geo_locations'])):
                specs['geo_locations'][i]['location_types'] = ['recent', 'home']

            # platform
            specs["publisher_platforms"] = [platform]

            # ---- All languages ---- #
            i_count += 1

            specs['languages'] = [None]

            file_out = os.path.join(specs_dir, 'specs' + str(i_count) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))

            # ---- Russian language ---- #
            i_count += 1

            specs['languages'] = [{'name': 'Russian', 'values': [17]}]

            file_out = os.path.join(specs_dir, 'specs' + str(i_count) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))
