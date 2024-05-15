import os
import json
import pandas as pd
import shutil
import numpy as np

# virtual machine and collection names
vm = 'stitch'
collection = 'israeli_conflict_homerecent'


if __name__ == '__main__':

    # ---- paths ---- #
    master_credentials_path = os.path.join('config', 'private', 'credentials_master.csv')
    specs_template_path = os.path.join('config', 'specs', 'templates')
    out_dir = os.path.join('docker', 'collectors', vm, collection)
    os.makedirs(out_dir, exist_ok=True)
    yagmail_path = os.path.join('config', 'private', 'yagmail.csv')

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

    # ---- yagmail credential ---- #
    if os.path.exists(yagmail_path):
        shutil.copy2(yagmail_path, os.path.join(out_dir, 'yagmail.csv'))

    # ---- collection specs ---- #

    # output directory
    specs_dir = os.path.join(out_dir, 'specs')
    os.makedirs(specs_dir, exist_ok=True)

    # cleanup old specs
    for f in os.listdir(specs_dir):
        os.remove(os.path.join(specs_dir, f))


    countries = ['IL', 'PS', 'EG', 'JO', 'LB', 'SY']
    drop_countries = ['SY']
    countries = [i for i in countries if i not in drop_countries]

    platforms = ['facebook', 'instagram']
    languages = {'hebrew':29, 'arabic':28}

    ps_cities = pd.read_csv('config/specs/specs_explore/targets_csv/city.csv')
    ps_cities = ps_cities.loc[ps_cities.country_code == 'PS']

    i = 0
    for country in countries:
        for platform in platforms:
            i += 1


            # all languages
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
                specs['geo_locations'][i]['location_types'] = None

            # age groups
            specs['ages_ranges'] = [
                {'min': 13}, {'min': 18}, {'min': 20}, {'min': 50}, {'min': 60},
                {'min': 13, 'max': 19}, {'min': 15, 'max': 49}, {'min': 15, 'max': 64}, {'min': 18, 'max': 34},
                {'min': 20, 'max': 59}, {'min': 20, 'max': 49}, {'min': 20, 'max': 29},
                {'min': 30, 'max': 39}, {'min': 40, 'max': 49}, {'min': 50, 'max': 59}
            ]

            # customise specs by platform and country
            specs["publisher_platforms"] = [platform]
            specs['languages'] = [None]

            file_out = os.path.join(specs_dir, '_'.join([str(i).zfill(2), country, platform]) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))


            # specific languages
            for language in languages.keys():
                i += 1

                specs_file = os.path.join(specs_template_path, country + '_regions.json')
                if not os.path.exists(specs_file):
                    print('Specs template does not exist: ' + specs_file)
                    continue

                # template json
                with open(specs_file) as f:
                    specs = json.load(f)
                specs['name'] = collection

                # age groups
                specs['ages_ranges'] = [
                    {'min': 13}, {'min': 18}, {'min': 20}, {'min': 60}, {'min': 65},
                    {'min': 13, 'max': 19}, {'min': 15, 'max': 49}, {'min': 15, 'max': 64}, {'min': 18, 'max': 34},
                    {'min': 20, 'max': 29}, {'min': 30, 'max': 39}, {'min': 40, 'max': 49}, {'min': 50, 'max': 59},
                    {'min': 60, 'max': 64}]

                # customise specs by platform and country
                specs["publisher_platforms"] = [platform]
                specs['languages'] = [{'name': language, 'values': [languages[language]]}]

                file_out = os.path.join(specs_dir, '_'.join([str(i).zfill(2), country, platform]) + '.json')
                with open(file_out, "w") as f:
                    f.write(json.dumps(specs))

