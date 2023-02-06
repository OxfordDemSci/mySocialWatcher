import os
import json
import pandas as pd

# virtual machine and collection names
vm = 'stitch'
collection = 'turkey_earthquake'


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
    countries = ['TR', 'SY']

    # output directory
    specs_dir = os.path.join(out_dir, 'specs')
    os.makedirs(specs_dir, exist_ok=True)

    # cleanup old specs
    for f in os.listdir(specs_dir):
        os.remove(os.path.join(specs_dir, f))

    i_count = 0

    for country in countries:
        # country = countries[0]

        # specs template json
        country_specs_template_path = os.path.join(specs_template_path, country + '_regions.json')

        # template json
        with open(country_specs_template_path) as f:
            specs = json.load(f)
        specs['name'] = collection

        # location types
        for i in range(len(specs['geo_locations'])):
            specs['geo_locations'][i]['location_types'] = ['recent', 'home']

        # ---- recent ----#

        # facebook
        i_count += 1

        specs["publisher_platforms"] = ['facebook']

        file_out = os.path.join(specs_dir, str(i_count).zfill(3) + '_' + country + '_facebook.json')
        with open(file_out, "w") as f:
            f.write(json.dumps(specs))

        # instagram
        i_count += 1

        specs["publisher_platforms"] = ['instagram']

        file_out = os.path.join(specs_dir, str(i_count).zfill(3) + '_' + country + '_instagram.json')
        with open(file_out, "w") as f:
            f.write(json.dumps(specs))

