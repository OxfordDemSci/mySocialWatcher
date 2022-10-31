import os
import json
import pandas as pd

# ---- settings ---- #

# virtual machine name
vm = 'example_virtual_machine'

# collection name
collection = 'example_collection'

# collection country
country = 'GB'

# specs template json
specs_template_path = os.path.join('deploy', 'specs', 'templates', country + '_regions.json')

# credentials master file
# (csv with required columns: vm, collection, token, app)
# (NOTE: use "./deploy/my/credentials_master.csv" to keep your tokens private)
# (i.e. private* file names and folders are in .gitignore)
master_credentials_path = os.path.join('deploy', 'credentials_master.csv')


if __name__ == '__main__':

    # ---- create credentials.csv ---- #

    # path for output credentials.csv
    credentials_path = os.path.join('deploy', 'docker', vm, collection, 'credentials.csv')

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
    specs_dir = os.path.join('deploy', 'docker', vm, collection, 'specs')
    os.makedirs(specs_dir, exist_ok=True)

    # load template json (to potentially modify)
    with open(specs_template_path) as f:
        specs = json.load(f)

    # write json to file
    file_out = os.path.join(specs_dir, 'specs1.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))
