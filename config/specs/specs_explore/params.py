from pathlib import Path

url = "https://graph.facebook.com/v18.0/search"
token = ''
params_all = {'behaviour': {'type': 'adTargetingCategory','class': 'behaviors','limit':1000,'access_token': token},
              'region':{'location_types':['region'],'type':'adgeolocation','q':'','limit':1000,'access_token': token},
              'country':{'location_types':['country'],'type':'adgeolocation','q':'','limit':1000,'access_token': token},
              'city':{'location_types':['city'],'type':'adgeolocation','q':'al','limit':1100,'access_token': token}}
def file_paths(spec_cat):
    json_file_path = Path.cwd()/f'config/specs/specs_explore/targets_json/{spec_cat}.json'
    csv_file_path = Path.cwd()/f'config/specs/specs_explore/targets_csv/{spec_cat}.csv'
    return json_file_path,csv_file_path
