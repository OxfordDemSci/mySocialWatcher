import os
import shutil
import json
import pandas as pd
from mysocialwatcher.specs.utils import dgg_specs

# virtual machine and collection
vm = 'badger'
collection = 'dgg_national'


if __name__ == '__main__':

    # ---- paths ---- #
    master_credentials_path = os.path.join('config', 'private', 'credentials_master.csv')
    specs_template_path = None
    env_template_path = os.path.join('config', 'private', 'collector.env')
    cron_template_path = os.path.join('config', 'cron', 'daily')
    out_dir = os.path.join('docker', 'virtual_machines', vm, collection)
    os.makedirs(out_dir, exist_ok=True)

    # ---- environment ---- #
    shutil.copy(src=env_template_path,
                dst=os.path.join(out_dir, '.env'))

    # ---- cron ---- #
    shutil.copy(src=cron_template_path,
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
