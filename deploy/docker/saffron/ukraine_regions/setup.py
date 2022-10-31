import os
import shutil
import json
import pandas as pd

if __name__ == '__main__':

    # ---- settings ---- #

    # virtual machine name
    vm = 'saffron'

    # collection name
    collection = 'ukraine_regions'

    # credentials master file
    master_credentials_path = os.path.join('deploy', 'private', 'credentials_master.csv')

    # specs template json
    specs_template_path = os.path.join('deploy', 'specs', 'templates', 'UA_regions.json')

    # ---- environment ---- #

    shutil.copy(src=os.path.join('deploy', 'private', '.env'),
                dst=os.path.join('deploy', 'docker', vm, collection, '.env'))

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

    # output directory
    out_dir = os.path.join('deploy', 'docker', vm, collection, 'specs')
    os.makedirs(out_dir, exist_ok=True)

    # template json
    with open(specs_template_path) as f:
        specs = json.load(f)

    # cleanup old specs
    for f in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, f))

    # ---- All languages ----#
    specs['languages'] = [None]

    # write to file
    file_out = os.path.join(out_dir, 'specs1.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))


    # ---- Ukrainian language ----#
    specs['languages'] = [{'name': 'Ukrainian', 'values': [52]}]

    # write to file
    file_out = os.path.join(out_dir, 'specs2.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))


    # ---- Russian language ---- #
    specs['languages'] = [{'name': 'Russian', 'values': [17]}]

    # write to file
    file_out = os.path.join(out_dir, 'specs3.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))


    # ---- All languages ['home', 'recent']----#
    specs['languages'] = [None]
    for i in range(len(specs.get('geo_locations'))):
        specs['geo_locations'][i]['location_types'] = [['home', 'recent']]

    # write to file
    file_out = os.path.join(out_dir, 'specs4.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))
