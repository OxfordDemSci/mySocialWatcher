import os
import json
import pandas as pd

# virtual machine and collection names
vm = 'stitch'
collection = 'westbank_cities'


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

    # full city list
    ps_cities = pd.read_csv('config/specs/specs_explore/targets_csv/city.csv')
    ps_cities = ps_cities.loc[ps_cities['country_code'].eq('PS') &
                              ps_cities['region'].eq('West Bank') &
                              ps_cities['type'].eq('city')]

    #-- template specs --#
    specs_file = os.path.join(specs_template_path, 'PS_regions.json')
    if not os.path.exists(specs_file):
        print('Specs template does not exist: ' + specs_file)

    # template json
    with open(specs_file) as f:
        specs = json.load(f)
    specs['name'] = collection

    platforms = ['facebook', 'instagram']
    languages = {'hebrew':29, 'arabic':28}

    # location types
    for i in range(len(specs['geo_locations'])):
        specs['geo_locations'][i]['location_types'] = ['recent']

    # cities
    for index, row in ps_cities.iterrows():
        specs['geo_locations'].append({
            "name": "cities",
            "values": [
                {
                    "key": row['key'],
                    "region": row['region'],
                    "region_id": row['region_id'],
                    "country_code": row['country_code'],
                    "name": row['name'],
                    "distance_unit": "kilometer",
                    "radius": 0
                }
            ],
            "location_types": [
                "recent"
            ]
        })

    i = 0
    for platform in platforms:
        i += 1

        #-- all languages --#
        specs["publisher_platforms"] = [platform]
        specs['languages'] = [None]

        file_out = os.path.join(specs_dir, '_'.join([str(i).zfill(2), platform, 'all']) + '.json')
        with open(file_out, "w") as f:
            f.write(json.dumps(specs))


        # specific languages
        for language in languages.keys():
            i += 1

            # customise specs by platform and country
            specs["publisher_platforms"] = [platform]
            specs['languages'] = [{'name': language, 'values': [languages[language]]}]

            file_out = os.path.join(specs_dir, '_'.join([str(i).zfill(2), platform, language]) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))

