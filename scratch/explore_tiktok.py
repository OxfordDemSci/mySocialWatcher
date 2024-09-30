# coding=utf-8
import json
import os

import requests
import pandas as pd
from six import string_types
from six.moves.urllib.parse import urlencode, urlunparse  # noqa
from dotenv import load_dotenv

load_dotenv(dotenv_path='./scratch/.env_tiktok')
secret = os.getenv('SECRET')
app_id = os.getenv('APP_ID')
auth_code = os.getenv('AUTH_CODE')

PATH = "/open_api/v1.3/oauth2/access_token/"

# 1. Get access_token
def build_url(path, query=""):
    # type: (str, str) -> str
    """
    Build request URL
    :param path: Request path
    :param query: Querystring
    :return: Request URL
    """
    scheme, netloc = "https", "business-api.tiktok.com"
    return urlunparse((scheme, netloc, path, "", query, ""))


def post(json_str):
    # type: (str) -> dict
    """
    Send POST request
    :param json_str: Args in JSON format
    :return: Response in JSON format
    """
    url = build_url(PATH)
    args = json.loads(json_str)
    headers = {
        "Content-Type": "application/json",
    }
    rsp = requests.post(url, headers=headers, json=args)
    return rsp.json()


# Args in JSON format
# my_args = "{\"secret\": \"%s\", \"app_id\": \"%s\", \"auth_code\": \"%s\"}" % (secret, app_id, auth_code)
# access_token = post(my_args)

access_token = os.getenv('ACCESS_TOKEN')

# Query audience count

url = 'https://business-api.tiktok.com/open_api/v1.3/ad/audience_size/estimate/'

headers = {
    'Access-Token': access_token,
    'Content-Type': 'application/json'
}
data = {
    "advertiser_id": '7381489555305775105',
    "objective_type": "REACH",
    "optimization_goal": "REACH",
    "placements": ["PLACEMENT_TIKTOK", "PLACEMENT_PANGLE", "PLACEMENT_GLOBAL_APP_BUNDLE"],
    "location_ids": [
        "3469034"
    ],
    "gender": "GENDER_UNLIMITED", # GENDER_MALE, GENDER_FEMALE
    "age_groups": ["AGE_18_24"]
}

response = requests.post(url, headers=headers, json=data)

print(response.json())



# List available regions
url = ' https://business-api.tiktok.com/open_api/v1.3/search/region/'

headers = {
    'Access-Token': access_token,
    'Content-Type': 'application/json'
}
params = {
    'advertiser_id': '7381489555305775105'
}

response = requests.get(url, headers=headers, params=params)

geolist = response.json()['data']['region_list']

geolist.to_csv('./config/specs/specs_explore/tiktok_regions_list.csv')

# endpoint `tool/region`: NOT WORKING
url = ' https://business-api.tiktok.com/open_api/v1.3/tool/region/'

headers = {
    'Access-Token': access_token,
    'Content-Type': 'application/json'
}
params = {
    'advertiser_id': '7381489555305775105',
    "objective_type": "REACH",
    "placements": ["PLACEMENT_TIKTOK"]
}

response = requests.get(url, headers=headers, params=params)
region = response.json()

# interest
url = 'https://business-api.tiktok.com/open_api/v1.3/targeting/search/'

headers = {
    'Access-Token': access_token,
    'Content-Type': 'application/json'
}
params = {
    'advertiser_id': '7381489555305775105',
    "targeting_type": "INTEREST_AND_BEHAVIOR"
}

interest = requests.get(url, headers=headers, params=params)
interest = interest.json()
interest = interest['data']
interest.keys()
general = pd.DataFrame.from_dict(interest['general_interest']['list_result'])
general.to_csv('./config/specs/specs_explore/tiktok_interest_list.csv')
