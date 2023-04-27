import os
import json
import pandas as pd

# virtual machine and collection names
vm = 'stitch'
collection = 'sudan_conflict'


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

    # output directory
    specs_dir = os.path.join(out_dir, 'specs')
    os.makedirs(specs_dir, exist_ok=True)

    # cleanup old specs
    for f in os.listdir(specs_dir):
        os.remove(os.path.join(specs_dir, f))


    countries = ['SD', 'TD', 'EG', 'CF', 'DJ', 'ER', 'ET', 'LY', 'SS', 'CD']
    drop_countries = []
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

            # customise specs by platform and country
            specs["publisher_platforms"] = [platform]
            specs['languages'] = [None]

            file_out = os.path.join(specs_dir, '_'.join([str(i), country, platform]) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))

