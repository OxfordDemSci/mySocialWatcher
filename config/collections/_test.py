import os
import shutil
import json
import pandas as pd

# ---- settings ---- #

# virtual machine name
vm = '_test'

# collection name
collection = '_test'


if __name__ == '__main__':

    # paths
    master_credentials_path = os.path.join('config', 'private', 'credentials_master.csv')
    env_template_path = os.path.join('config', 'private', 'collector.env')
    specs_template_path = os.path.join('config', 'specs', '_test.json')
    cron_template_path = os.path.join('config', 'cron', 'daily')
    out_dir = os.path.join('docker', 'collectors', vm, collection)
    os.makedirs(out_dir, exist_ok=True)

    # ---- environment ---- #

    shutil.copy(src=env_template_path,
                dst=os.path.join(out_dir, '.env'))

    # ---- cron ---- #

    shutil.copy(src=cron_template_path,
                dst=os.path.join(out_dir, 'cronjob'))

    # ---- create credentials.csv ---- #

    # path for output credentials.csv
    credentials_path = os.path.join(out_dir, 'credentials.csv')

    # load master credentials
    master_credentials = pd.read_csv(master_credentials_path)

    # filter vm and collection
    credentials = master_credentials.loc[(master_credentials.vm == vm) & (master_credentials.collection == collection)]

    # save to csv
    credentials.to_csv(credentials_path,
                       columns=['token', 'app'],
                       header=False,
                       index=False)

    # ---- create collection specs ---- #

    # output directory
    specs_dir = os.path.join(out_dir, 'specs')
    os.makedirs(specs_dir, exist_ok=True)

    # load template json
    with open(specs_template_path) as f:
        specs = json.load(f)

    # modify template json (no modification shown here)
    pass

    # write json to file
    file_out = os.path.join(specs_dir, 'specs001.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))
