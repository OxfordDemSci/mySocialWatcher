from pysocialwatcher import watcherAPI, constants
import json
import os

credentials_path = './docker/collectors/jubal/baseline/credentials.csv'

countries = ['AF', 'BD', 'BF', 'BR', 'CD', 'CM', 'CO', 'CU', 'EC', 'ET', 'GH', 'GN', 'GT', 'HT', 'IL', 'IQ', 'IN',
             'LY', 'ML', 'MM', 'MZ', 'NE', 'NG', 'NP', 'PE', 'PK', 'PS', 'SD', 'SL', 'SO', 'SS', 'SY', 'UA', 'VE', 'YE',
             'ZA', 'ZM']

watcher = watcherAPI(api_version='15.0',
                     sleep_time=12,
                     save_every_x=100)

# load credentials
watcher.load_credentials_file(credentials_path)
watcher.check_tokens_account_valid()

# data path
data_dir = './data/tmp'

for country in countries:
    # country = countries[0]

    specs = {"name": "test",
             "geo_locations": [{"name": "countries", "values": [country], "location_types": ["recent"]}],
             "ages_ranges": [{"min": 13}],
             "genders": [0],
             "publisher_platforms": ["facebook"]}

    specs_json = json.dumps(specs)
    with open(os.path.join(data_dir, 'specs.json'), 'w') as f:
        f.write(specs_json)

    df = watcher.run_data_collection(
        json_input_file_path=os.path.join(data_dir, 'specs.json'),
        output_dir=data_dir + '/',
        remove_tmp_files=True)

