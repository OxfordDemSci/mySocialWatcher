import copy
import os
import copy
import json
import shutil
import pandas as pd
import numpy as np

# virtual machine and collection
vm = 'mingo'
collection = 'venezuelan_exodus2'


if __name__ == '__main__':

    # ---- paths ---- #
    master_credentials_path = os.path.join('config', 'private', 'credentials_master.csv')
    specs_template_path = os.path.join('config', 'specs', 'examples', 'venezuelan_exodus.json')
    out_dir = os.path.join('docker', 'collectors', vm, collection)
    os.makedirs(out_dir, exist_ok=True)
    yagmail_path = os.path.join('config', 'private', 'yagmail.csv')

    # ---- yagmail credential ---- #
    if os.path.exists(yagmail_path):
        shutil.copy2(yagmail_path, os.path.join(out_dir, 'yagmail.csv'))

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
    credentials['app'] = credentials['app'].astype(np.int64)

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

    # load template json
    with open(specs_template_path) as f:
        specs_template = json.load(f)

    # location types
    for i in range(len(specs_template['geo_locations'])):
        if 'location_types' in specs_template['geo_locations'][i].keys():
            del specs_template['geo_locations'][i]['location_types']

    # modify template json
    # (no modification shown here other than defining the name of the collection)
    specs_template['name'] = collection

    # check if geo_location includes multiple countries
    def check_multi_country(loc):
        country_list = []
        if loc.get('name') == 'countries':
            country_list += list(set(loc.get('values')))
        else:
            country_list += [v.get('country') for v in loc.get('values')]
            country_list += [v.get('country_codes') for v in loc.get('values')]
        country_list = list(set(country_list))
        country_list = [i for i in country_list if i is not None]
        if len(country_list) > 1:
            raise Exception('Location with more than one country: ' + str(loc))

    # get country name from geo_location
    def country_from_location(loc):
        check_multi_country(loc)
        if loc.get('name') == 'countries':
            country = loc.get('values')[0]
        elif 'country' in loc.get('values')[0].keys():
            country = loc.get('values')[0].get('country')
        elif 'country_code' in loc.get('values')[0].keys():
            country = loc.get('values')[0].get('country_code')
        return country

    # ---- specs: region-level ---- #

    # identify countries with regional data
    countries = []
    for i in range(len(specs_template.get('geo_locations'))):
        loc = specs_template.get('geo_locations')[i]
        check_multi_country(loc)
        if loc.get('name') == 'regions':
            if 'country_code' in loc.get('values')[0].keys():
                countries.append(loc.get('values')[0].get('country_code'))
            elif 'country' in loc.get('values')[0].keys():
                countries.append(loc.get('values')[0].get('country'))
    countries = list(set(countries))

    # exclude CO because it is included in a separate collection
    countries = [i for i in countries if i != 'CO']

    for i in range(len(countries)):
        specs = copy.deepcopy(specs_template)
        specs['geo_locations'] = []
        for j in range(len(specs_template.get('geo_locations'))):
            loc = specs_template.get('geo_locations')[j]
            country = country_from_location(loc)
            if country == countries[i] and loc.get('name') == 'regions':
                specs['geo_locations'].append(loc)

        # write json to file
        file_out = os.path.join(specs_dir, '1_ven_exodus_regions_' + countries[i] + '.json')
        with open(file_out, "w") as f:
            f.write(json.dumps(specs))

    # ---- specs: country-level ---- #
    specs = copy.deepcopy(specs_template)
    specs['geo_locations'] = []
    for i in range(len(specs_template.get('geo_locations'))):
        loc = specs_template.get('geo_locations')[i]
        country = country_from_location(loc)
        if country != 'CO' and loc.get('name') == 'countries':
            specs['geo_locations'].append(loc)

    # write json to file
    file_out = os.path.join(specs_dir, '2_ven_exodus_countries.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))

    # ---- specs: city-level ---- #
    specs = copy.deepcopy(specs_template)
    specs['geo_locations'] = []
    for i in range(len(specs_template.get('geo_locations'))):
        loc = specs_template.get('geo_locations')[i]
        country = country_from_location(loc)
        if country != 'CO' and loc.get('name') in ['cities', 'custom_locations']:
            specs['geo_locations'].append(loc)

    # write json to file
    file_out = os.path.join(specs_dir, '3_ven_exodus_cities.json')
    with open(file_out, "w") as f:
        f.write(json.dumps(specs))


