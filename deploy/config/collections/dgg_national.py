import os
import shutil
import json
import pandas as pd
from mysocialwatcher.specs.utils import dgg_specs

if __name__ == '__main__':

    # virtual machine name
    vm = 'badger'

    # collection name
    collection = 'dgg_national'

    # make directory
    out_dir = os.path.join('deploy', 'docker', vm, collection)
    os.makedirs(out_dir, exist_ok=True)

    # credentials master file
    master_credentials_path = os.path.join('deploy', 'private', 'credentials_master.csv')

    # ---- environment ---- #

    shutil.copy(src=os.path.join('deploy', 'config', 'private', 'collector.env'),
                dst=os.path.join(out_dir, '.env'))

    # ---- cron ---- #

    shutil.copy(src=os.path.join('deploy', 'config', 'daily'),
                dst=os.path.join(out_dir, 'cronjob'))

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

    # specs json
    specs = dgg_specs()

    file_out = os.path.join(specs_dir, 'specs1.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))
