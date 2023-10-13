from pysocialwatcher import watcherAPI, constants
import json
import os

credentials_path = os.path.join('scratch','private_credentials.csv')

countries = ['PS']

watcher = watcherAPI(api_version='17.0',
                     sleep_time=12,
                     save_every_x=100)

# load credentials
watcher.load_credentials_file(credentials_path)
watcher.check_tokens_account_valid()

# data path
data_dir = os.path.join('data','tmp')

for country in countries:
    # country = countries[0]

    specs_countries = {
        "name": "test",
        "geo_locations": [
            {
                "name": "countries",
                "values": [
                    "PS"
                ],
                "location_types": [
                    "home", "recent"
                ]
            }
        ],
        "ages_ranges": [{"min": 13}],
        "genders": [0],
        "publisher_platforms": ["facebook"]}

    specs_regions = {"name": "test",
             "geo_locations": [
                 {
                     "name": "regions",
                     "values": [
                         {
                             "key": 4996,
                             "country_code": "PS",
                             "name": "West Bank"
                         }
                     ],
                     "location_types": [
                         "recent"
                     ]
                 },
                 {
                     "name": "regions",
                     "values": [
                         {
                             "key": 4997,
                             "country_code": "PS",
                             "name": "Gaza Strip"
                         }
                     ],
                     "location_types": [
                         "recent"
                     ]
                 }
             ],
             "ages_ranges": [{"min": 13}],
             "genders": [0],
             "publisher_platforms": ["facebook"]}

    specs_cities = {"name": "test",
             "geo_locations": [
                 {
                     "name": "cities",
                     "values": [
                         {
                             "key": 2673755,
                             "region": "West Bank",
                             "region_id": 4996,
                             "country_code": "PS",
                             "name": "Jericho",
                             "distance_unit": "kilometer",
                             "radius": 0
                         }
                     ],
                     "location_types": [
                         "recent"
                     ]
                 },
                 {
                     "name": "cities",
                     "values": [
                         {
                             "key": 2673765,
                             "region": "Gaza Strip",
                             "region_id": 4997,
                             "country_code": "PS",
                             "name": "Gaza City",
                             "distance_unit": "kilometer",
                             "radius": 0
                         }
                     ],
                     "location_types": [
                         "recent"
                     ]
                 }
             ],
             "ages_ranges": [{"min": 13}],
             "genders": [0],
             "publisher_platforms": ["facebook"]}

    specs = {"name": "test",
             "geo_locations": [

             ],
             "ages_ranges": [{"min": 13}],
             "genders": [0],
             "publisher_platforms": ["facebook"]}


    specs_json = json.dumps(specs_countries)
    with open(os.path.join(data_dir, 'specs.json'), 'w') as f:
        f.write(specs_json)

    df = watcher.run_data_collection(
        json_input_file_path=os.path.join(data_dir, 'specs.json'),
        output_dir=data_dir + '/',
        remove_tmp_files=True)

