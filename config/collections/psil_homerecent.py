import os
import json
import pandas as pd

# virtual machine and collection names
vm = 'stitch'
collection = 'psil_homerecent'


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

    # reset specs counter
    specs_count = 0

    #---- israeli_conflict ----#
    countries = ['IL', 'PS', 'EG', 'JO', 'LB', 'SY']
    drop_countries = ['SY']
    countries = [i for i in countries if i not in drop_countries]

    platforms = ['facebook', 'instagram']
    languages = {'hebrew':29, 'arabic':28}

    for country in countries:
        # country = countries[0]

        # define template
        specs_file = os.path.join(specs_template_path, country + '_regions.json')
        if not os.path.exists(specs_file):
            print('Specs template does not exist: ' + specs_file)
            continue

        # load template json
        with open(specs_file) as f:
            specs = json.load(f)

        # collection name
        specs['name'] = collection

        # location types
        for i in range(len(specs['geo_locations'])):
            specs['geo_locations'][i]['location_types'] = ['home', 'recent']

        # age groups
        specs['ages_ranges'] = [
            {'min': 13}, {'min': 18}, {'min': 20}, {'min': 60}, {'min': 65},
            {'min': 13, 'max': 19}, {'min': 15, 'max': 49}, {'min': 15, 'max': 64}, {'min': 18, 'max': 34},
            {'min': 20, 'max': 29}, {'min': 30, 'max': 39}, {'min': 40, 'max': 49}, {'min': 50, 'max': 59},
            {'min': 60, 'max': 64}]


        for platform in platforms:
            # platform = platforms[0]
            specs_count += 1

            # customise specs
            specs["publisher_platforms"] = [platform]
            specs['languages'] = [None]

            file_out = os.path.join(specs_dir, '_'.join([str(specs_count).zfill(2), 'israeli_conflict', country, platform]) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))


            # specific languages
            for language in languages.keys():
                specs_count += 1

                # customise specs
                specs['languages'] = [{'name': language, 'values': [languages[language]]}]

                file_out = os.path.join(specs_dir, '_'.join([str(specs_count).zfill(2), 'israeli_conflict', country, platform, language]) + '.json')
                with open(file_out, "w") as f:
                    f.write(json.dumps(specs))

    #---- gaza cities ----#

    # full city list
    ps_cities = pd.read_csv('config/specs/specs_explore/targets_csv/city.csv')
    ps_cities = ps_cities.loc[ps_cities['country_code'].eq('PS') &
                              ps_cities['type'].eq('city') &
                              ps_cities['region'].eq('Gaza Strip')]

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

    # age groups
    specs['ages_ranges'].append({'min': 18, 'max': 34})

    for platform in platforms:
        specs_count += 1

        #-- all languages --#
        specs["publisher_platforms"] = [platform]
        specs['languages'] = [None]

        file_out = os.path.join(specs_dir, '_'.join([str(specs_count).zfill(2), 'gaza_cities', platform]) + '.json')
        with open(file_out, "w") as f:
            f.write(json.dumps(specs))


        # specific languages
        for language in languages.keys():
            specs_count += 1

            # customise specs by platform and country
            specs["publisher_platforms"] = [platform]
            specs['languages'] = [{'name': language, 'values': [languages[language]]}]

            file_out = os.path.join(specs_dir, '_'.join([str(specs_count).zfill(2), 'gaza_cities', platform, language]) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))


    #---- lebanon cities ----#

    # full city list
    cities = pd.read_csv('config/specs/specs_explore/targets_csv/city.csv')
    cities = cities.loc[cities['country_code'].eq('LB') &
                        cities['type'].eq('city')]
    # cities['region_id'].isin([2061, 4322])
    cities.drop_duplicates(subset='key', keep=False, inplace=True)

    # -- template specs --#
    specs_file = os.path.join(specs_template_path, 'LB_regions.json')
    if not os.path.exists(specs_file):
        print('Specs template does not exist: ' + specs_file)

    # template json
    with open(specs_file) as f:
        specs = json.load(f)
    specs['name'] = collection

    platforms = ['facebook', 'instagram']
    languages = {}  # {'arabic': 28, 'hebrew': 29}

    # cities
    specs['geo_locations'] = []
    for index, row in cities.iterrows():
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

    # age groups
    specs['ages_ranges'] = [
        {'min': 13}, {'min': 18}, {'min': 20}, {'min': 60}, {'min': 65},
        {'min': 13, 'max': 19}, {'min': 15, 'max': 49}, {'min': 15, 'max': 64}, {'min': 18, 'max': 34},
        {'min': 20, 'max': 29}, {'min': 30, 'max': 39}, {'min': 40, 'max': 49}, {'min': 50, 'max': 59},
        {'min': 60, 'max': 64}]

    for platform in platforms:
        specs_count += 1

        # -- all languages --#
        specs["publisher_platforms"] = [platform]
        specs['languages'] = [None]

        file_out = os.path.join(specs_dir, '_'.join([str(specs_count).zfill(2), 'lebanon_cities', platform]) + '.json')
        with open(file_out, "w") as f:
            f.write(json.dumps(specs))

        # specific languages
        for language in languages.keys():
            specs_count += 1

            # customise specs by platform and country
            specs["publisher_platforms"] = [platform]
            specs['languages'] = [{'name': language, 'values': [languages[language]]}]

            file_out = os.path.join(specs_dir, '_'.join([str(specs_count).zfill(2), 'lebanon_cities', platform, language]) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))


    #---- west bank cities ----#

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

    # cities
    specs['geo_locations'] = []
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

    # age groups
    specs['ages_ranges'] = [
        {'min': 13}, {'min': 18}, {'min': 20}, {'min': 60}, {'min': 65},
        {'min': 13, 'max': 19}, {'min': 15, 'max': 49}, {'min': 15, 'max': 64}, {'min': 18, 'max': 34},
        {'min': 20, 'max': 29}, {'min': 30, 'max': 39}, {'min': 40, 'max': 49}, {'min': 50, 'max': 59},
        {'min': 60, 'max': 64}]

    for platform in platforms:
        specs_count += 1

        #-- all languages --#
        specs["publisher_platforms"] = [platform]
        specs['languages'] = [None]

        file_out = os.path.join(specs_dir, '_'.join([str(specs_count).zfill(2), 'westbank_cities', platform]) + '.json')
        with open(file_out, "w") as f:
            f.write(json.dumps(specs))


        # specific languages
        for language in languages.keys():
            specs_count += 1

            # customise specs by platform and country
            specs["publisher_platforms"] = [platform]
            specs['languages'] = [{'name': language, 'values': [languages[language]]}]

            file_out = os.path.join(specs_dir, '_'.join([str(specs_count).zfill(2), 'westbank_cities', platform, language]) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))


    #---- israeli cities ----#

    # full city list
    cities = pd.read_csv('config/specs/specs_explore/targets_csv/city.csv')
    cities = cities.loc[cities['country_code'].eq('IL') &
                        cities['type'].eq('city')]
    cities.drop_duplicates(subset='key', keep=False, inplace=True)

    # -- template specs --#
    specs_file = os.path.join(specs_template_path, 'IL_regions.json')
    if not os.path.exists(specs_file):
        print('Specs template does not exist: ' + specs_file)

    # template json
    with open(specs_file) as f:
        specs = json.load(f)
    specs['name'] = collection

    platforms = ['facebook', 'instagram']
    languages = {'hebrew': 29, 'arabic': 28}

    # cities
    specs['geo_locations'] = []
    for index, row in cities.iterrows():
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

    # age groups
    specs['ages_ranges'] = [
        {'min': 13}, {'min': 18}, {'min': 20}, {'min': 60}, {'min': 65},
        {'min': 13, 'max': 19}, {'min': 15, 'max': 49}, {'min': 15, 'max': 64}, {'min': 18, 'max': 34},
        {'min': 20, 'max': 29}, {'min': 30, 'max': 39}, {'min': 40, 'max': 49}, {'min': 50, 'max': 59},
        {'min': 60, 'max': 64}]

    for platform in platforms:
        specs_count += 1

        # -- all languages --#
        specs["publisher_platforms"] = [platform]
        specs['languages'] = [None]

        file_out = os.path.join(specs_dir, '_'.join([str(specs_count).zfill(2), 'israeli_cities', platform]) + '.json')
        with open(file_out, "w") as f:
            f.write(json.dumps(specs))

        # specific languages
        for language in languages.keys():
            specs_count += 1

            # customise specs by platform and country
            specs["publisher_platforms"] = [platform]
            specs['languages'] = [{'name': language, 'values': [languages[language]]}]

            file_out = os.path.join(specs_dir, '_'.join([str(specs_count).zfill(2), 'israeli_cities', platform, language]) + '.json')
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))
