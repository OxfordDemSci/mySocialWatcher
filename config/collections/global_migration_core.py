import os
import shutil
import pandas as pd
import numpy as np

# virtual machine and collection
vm = 'jubal'
collection = 'global_migration_core'


if __name__ == '__main__':

    # ---- paths ---- #
    master_credentials_path = os.path.join('config', 'private', 'credentials_master.csv')
    specs_template_path = os.path.join('config', 'specs', 'examples', 'global_migration')

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
    credentials["app"] = credentials["app"].astype(np.int64)

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

    specs = os.listdir(specs_template_path)
    for spec in specs:
        shutil.copy(os.path.join(specs_template_path, spec), os.path.join(specs_dir, spec))

    # ---- yagmail credential ---- #
    if os.path.exists(yagmail_path):
        shutil.copy2(yagmail_path, os.path.join(out_dir, 'yagmail.csv'))
