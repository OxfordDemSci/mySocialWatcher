# -*- coding: utf-8 -*-
import json
from tabulate import tabulate
import pandas as pd
from . import constants
import itertools
import logging
import coloredlogs
import time
from multiprocessing import Process, Manager
import numpy
import requests
import ast
import os

coloredlogs.install(level=logging.INFO)


class RequestException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class JsonFormatException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FatalException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def print_error_warning(error_json, params):
    print_warning("Facebook Error Code: " + str(error_json["error"]["code"]))
    print_warning("Facebook Error Message: " + str(error_json["error"]["message"]))
    if "error_user_title" in error_json["error"] and "error_user_msg" in error_json["error"]:
        print_warning("Facebook: " + str(error_json["error"]["error_user_title"]) + "\n" + str(
            error_json["error"]["error_user_msg"]))
    print_warning("Facebook Trace Id: " + str(error_json["error"]["fbtrace_id"]))
    print_warning("Request Params : " + str(params))


def get_dataframe_from_json_response_query_data(json_response):
    dataframe = pd.DataFrame()
    for entry in json_response["data"]:
        entry_details = {}
        for field in constants.DETAILS_FIELD_FROM_FACEBOOK_TARGETING_SEARCH:
            entry_details[field] = entry[field] if field in entry else None
        dataframe = dataframe.append(entry_details, ignore_index=True)
    return dataframe


def handle_send_request_error(response, url, params, tryNumber):
    try:
        error_json = json.loads(response.text)
        if error_json["error"]["code"] == constants.API_UNKOWN_ERROR_CODE_1 or error_json["error"][
            "code"] == constants.API_UNKOWN_ERROR_CODE_2:
            print_error_warning(error_json, params)
            time.sleep(constants.INITIAL_TRY_SLEEP_TIME * tryNumber)
            return send_request(url, params, tryNumber)
        elif error_json["error"]["code"] == constants.INVALID_PARAMETER_ERROR and "error_subcode" in error_json[
            "error"] and error_json["error"]["error_subcode"] == constants.FEW_USERS_IN_CUSTOM_LOCATIONS_SUBCODE_ERROR:
            return get_fake_response()
        elif "message" in error_json["error"] and "Invalid zip code" in error_json["error"][
            "message"] and constants.INGORE_INVALID_ZIP_CODES:
            print_warning("Invalid Zip Code:" + str(params[constants.TARGETING_SPEC_FIELD]))
            return get_fake_response()
        else:
            logging.error("Could not handle error.")
            logging.error("Error Code:" + str(error_json["error"]["code"]))
            if "message" in error_json["error"]:
                logging.error("Error Message:" + str(error_json["error"]["message"]))
            if "error_subcode" in error_json["error"]:
                logging.error("Error Subcode:" + str(error_json["error"]["error_subcode"]))
            raise FatalException(str(error_json["error"]))
    except Exception as e:
        logging.error(e)
        raise FatalException(str(response.text))


def send_request(url, params, tryNumber=0):
    tryNumber += 1
    if tryNumber >= constants.MAX_NUMBER_TRY:
        print_warning("Maximum Number of Tries reached. Failing.")
        raise FatalException("Maximum try reached.")
    try:
        response = requests.get(url, params=params, timeout=constants.REQUESTS_TIMEOUT)
    except Exception as error:
        raise RequestException(error.message)
    if response.status_code == 200:
        return response
    else:
        return handle_send_request_error(response, url, params, tryNumber)


def call_request_fb(row, token, account, url):
    target_request = row[constants.TARGETING_FIELD]
    payload = {
        'optimization_goal': "AD_RECALL_LIFT",
        'targeting_spec': json.dumps(target_request),
        'access_token': token,
    }
    payload_str = str(payload)
    print_warning("\tSending in request: %s" % (payload_str))
    url = url.format(account)
    response = send_request(url, payload)

    if "x-business-use-case-usage" in response.headers:
        usage_dict = ast.literal_eval(response.headers["x-business-use-case-usage"])[account][0]
        print_warning("\tUsage Stats: Call count (%d), cputime (%d), total_time (%d)." % (usage_dict["call_count"],
                                                                                          usage_dict["total_cputime"],
                                                                                          usage_dict["total_time"]))
    return response.content


def get_fake_response():
    response = requests.models.Response()
    response._content = constants.FAKE_DATA_RESPONSE_CONTENT
    response.status_code = 200
    logging.warn("Fake Response created: " + response.content)
    return response


def trigger_facebook_call(index, row, token, account, shared_queue, url):
    try:
        response = call_request_fb(row, token, account, url)
        shared_queue.put((index, response))
    except RequestException:
        print_warning("Warning Facebook Request Failed")
        print_warning("Row: " + str(row))
        print_warning("It will try again later")
        shared_queue.put((index, numpy.nan))


#    except Exception, e:
#        print_warning("request failed because %s"%(e))


def add_mocked_column(dataframe):
    dataframe["mock_response"] = dataframe["response"].apply(
        lambda response: True if (constants.MOCK_RESPONSE_FIELD in str(response)) else False)
    return dataframe


def add_timestamp(dataframe):
    dataframe["timestamp"] = constants.UNIQUE_TIME_ID
    return dataframe


def add_published_platforms(dataframe, input_json):
    platforms = constants.PUBLISHER_PLATFORM_DEFAULT
    if constants.API_PUBLISHER_PLATFORMS_FIELD in input_json:
        platforms = input_json[constants.API_PUBLISHER_PLATFORMS_FIELD]
    dataframe[constants.API_PUBLISHER_PLATFORMS_FIELD] = json.dumps(platforms)
    return dataframe


def trigger_request_process_and_return_response(rows_to_request, url):
    process_manager = Manager()
    shared_queue = process_manager.Queue()
    shared_queue_list = []

    # Trigger Process in rows
    for index, row in rows_to_request.iterrows():
        token, account = get_token_and_account_number_or_wait()
        p = Process(target=trigger_facebook_call, args=(index, row, token, account, shared_queue, url))
        p.start()
        p.join()

    # Put things from shared list to normal list
    while shared_queue.qsize() != 0:
        shared_queue_list.append(shared_queue.get())
    return shared_queue_list


def check_exception(p):
    if p.exitcode != 0:
        raise FatalException("FatalError: Check logging for clue. No way to proceed from here.")


def print_info(message):
    logging.info(message)


def unstrict_literal_eval(string):
    try:
        value = ast.literal_eval(string)
        return value
    except ValueError:
        return string
    except SyntaxError:
        return string


def load_dataframe_from_file(file_path):
    dataframe = pd.read_csv(file_path)
    return dataframe.applymap(unstrict_literal_eval)


def save_response_in_dataframe(shared_queue_list, df):
    for result_tuple in shared_queue_list:
        result_index = result_tuple[0]
        result_response = result_tuple[1]
        df.loc[result_index, "response"] = result_response
        df.loc[result_index, "timestamp"] = str(time.time()).split(".")[0]


def save_skeleton_dataframe(dataframe, output_dir=""):
    print_info("Saving Skeleton file: " + constants.DATAFRAME_SKELETON_FILE_NAME)
    dataframe.to_csv(output_dir + constants.DATAFRAME_SKELETON_FILE_NAME)


def save_temporary_dataframe(dataframe, output_dir=""):
    print_info("Saving temporary file: " + constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME)
    dataframe.to_csv(output_dir + constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME)


def save_after_collecting_dataframe(dataframe, output_dir=""):
    print_info("Saving after collecting file: " + constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME)
    dataframe.to_csv(output_dir + constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME)


def save_after_collecting_dataframe_without_full_response(dataframe, output_dir=""):
    dataframe = dataframe.drop('response', 1)
    print_dataframe(dataframe)
    print_info("Saving after collecting file: " + constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME_WITHOUT_FULL_RESPONSE)
    dataframe.to_csv(output_dir + constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME_WITHOUT_FULL_RESPONSE)


def remove_temporary_dataframes(output_dir=""):
    if os.path.exists(output_dir + constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME):
        for file in [constants.DATAFRAME_SKELETON_FILE_NAME, constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME]:
            os.remove(output_dir + file)


def print_warning(message):
    logging.warn(message)


def load_json_data_from_response(response):
    return json.loads(response.content)


def print_dataframe(df):
    print(tabulate(df, headers='keys', tablefmt='psql', floatfmt=".0f"))


def build_initial_collection_dataframe():
    return pd.DataFrame(columns=constants.DATAFRAME_COLUMNS)


def get_all_combinations_from_input(input_data_json):
    to_combine_fields = {}
    for field in constants.INPUT_FIELDS_TO_COMBINE:
        try:
            if isinstance(input_data_json[field], list):
                field_content = input_data_json[field]
                to_combine_fields[field] = field_content
            if isinstance(input_data_json[field], dict):
                for intra_field_key in list(input_data_json[field].keys()):
                    to_combine_fields[intra_field_key] = input_data_json[field][intra_field_key]

        except KeyError:
            if constants.VERBOSE:
                print_warning("Field not expecified: " + field)

    for field in list(to_combine_fields.keys()):
        for index, value in enumerate(to_combine_fields[field]):
            to_combine_fields[field][index] = (field, value)
    all_combinations = list(itertools.product(*list(to_combine_fields.values())))
    return all_combinations


def add_list_of_ANDS_to_input(list_of_ANDS_between_groups, input_data_json):
    for interests_to_AND in list_of_ANDS_between_groups:
        names = []
        and_ors = []
        for interest_to_AND in interests_to_AND:
            names.append(interest_to_AND[constants.INPUT_NAME_FIELD])
            if "or" not in interest_to_AND:
                raise Exception("Only AND of ors are supported")
            and_ors.append(interest_to_AND["or"])
        new_and_interest = {
            constants.INPUT_NAME_FIELD: " AND ".join(names),
            "and_ors": and_ors,
            "isAND": True
        }
        input_data_json[constants.INPUT_INTEREST_FIELD].append(new_and_interest)


def generate_collection_request_from_combination(current_combination, input_data):
    targeting = build_targeting(current_combination, input_data)
    dataframe_row = {}
    for field in current_combination:
        field_name = field[0]
        value = field[1]
        dataframe_row[field_name] = value
    dataframe_row[constants.ALLFIELDS_FIELD] = current_combination
    dataframe_row[constants.TARGETING_FIELD] = targeting
    dataframe_row[constants.INPUT_NAME_FIELD] = input_data[constants.INPUT_NAME_FIELD]
    return dataframe_row


def select_common_fields_in_targeting(targeting, input_combination_dictionary):
    # Selecting Geolocation
    geo_location = input_combination_dictionary[constants.INPUT_GEOLOCATION_FIELD]
    if constants.INPUT_GEOLOCATION_LOCATION_TYPE_FIELD in geo_location:
        location_type = geo_location[constants.INPUT_GEOLOCATION_LOCATION_TYPE_FIELD]
    else:
        location_type = constants.DEFAULT_GEOLOCATION_LOCATION_TYPE_FIELD

    targeting[constants.API_GEOLOCATION_FIELD] = {
        geo_location["name"]: geo_location["values"],
        constants.INPUT_GEOLOCATION_LOCATION_TYPE_FIELD: location_type
    }
    # Selecting Age
    age_range = input_combination_dictionary[constants.INPUT_AGE_RANGE_FIELD]
    targeting[constants.API_MIN_AGE_FIELD] = age_range[constants.MIN_AGE] if constants.MIN_AGE in age_range else None
    targeting[constants.API_MAX_AGE_FIELD] = age_range[constants.MAX_AGE] if constants.MAX_AGE in age_range else None

    # Selecting genders
    gender = input_combination_dictionary[constants.INPUT_GENDER_FIELD]
    targeting[constants.API_GENDER_FIELD] = [gender]

    # Selecting Languages
    if constants.INPUT_LANGUAGE_FIELD in input_combination_dictionary:
        languages = input_combination_dictionary[constants.INPUT_LANGUAGE_FIELD]
        if languages:
            targeting[constants.API_LANGUAGES_FIELD] = languages["values"]
    elif constants.VERBOSE:
        print_warning("No field: " + constants.INPUT_LANGUAGE_FIELD)


def get_api_field_name(field_name):
    return constants.INPUT_TO_API_FIELD_NAME[field_name]


def process_dau_audience_from_response(literal_response):
    aud = json.loads(literal_response)["data"][0]
    audience = aud["estimate_dau"]
    return int(audience)


def process_mau_audience_from_response(literal_response):
    aud = json.loads(literal_response)["data"][0]
    if "estimate_mau" in aud:
        audience=int(aud["estimate_mau"])
    else:
        audience=None
    return audience

def process_mau_upper_audience_from_response(literal_response):
    aud = json.loads(literal_response)["data"][0]
    audience=aud["estimate_mau_upper_bound"]
    return int(audience)


def process_mau_lower_audience_from_response(literal_response):
    aud = json.loads(literal_response)["data"][0]
    audience=aud["estimate_mau_lower_bound"]
    return int(audience)


def post_process_collection(collection_dataframe):
    # For now just capture audience
    print_info("Computing Audience and DAU column")
    collection_dataframe["dau_audience"] = collection_dataframe["response"].apply(
        lambda x: process_dau_audience_from_response(x))

    collection_dataframe["mau_audience"] = collection_dataframe["response"].apply(
        lambda x: process_mau_audience_from_response(x))

    collection_dataframe["mau_audience_upper_bound"] = collection_dataframe["response"].apply(
        lambda x: process_mau_upper_audience_from_response(x))

    collection_dataframe["mau_audience_lower_bound"] = collection_dataframe["response"].apply(
        lambda x: process_mau_lower_audience_from_response(x))
    
    collection_dataframe = add_mocked_column(collection_dataframe)
    return collection_dataframe


def select_advance_targeting_type_array_ids(segment_type, input_value, targeting):
    api_field_name = get_api_field_name(segment_type)
    if input_value:
        if "or" in input_value:
            or_query = []
            for or_id in input_value["or"]:
                or_query.append({"id": or_id})
            targeting["flexible_spec"].append({api_field_name: or_query})

        if "and" in input_value:
            for id_and in input_value["and"]:
                ## TODO: make the behavior AND query request less hacky
                if(segment_type == constants.INPUT_BEHAVIOR_FIELD or segment_type == constants.INPUT_INCOME_FIELD):
                    if(len(targeting['flexible_spec']) == 1):
                        targeting['flexible_spec'].append({api_field_name : []})
                    targeting['flexible_spec'][1][api_field_name].append({"id" : id_and})
                else:
                    targeting["flexible_spec"].append({segment_type: {"id": id_and}})

        if "not" in input_value:
            if not "exclusions" in targeting:
                targeting["exclusions"] = {}
            if not api_field_name in list(targeting["exclusions"].keys()):
                targeting["exclusions"][api_field_name] = []
            for id_not in input_value["not"]:
                targeting["exclusions"][api_field_name].append({"id": id_not})

        if "and_ors" in input_value:
            for or_ids in input_value["and_ors"]:
                or_query = []
                for or_id in or_ids:
                    or_query.append({"id": or_id})
                targeting["flexible_spec"].append({segment_type: or_query})

        if "or" not in input_value and "and" not in input_value and "not" not in input_value and "and_ors" not in input_value:
            raise JsonFormatException("Something wrong with: " + str(input_value))


def get_interests_by_group_to_AND(input_data_json, groups_ids):
    interests_by_group_to_AND = {}
    for group_id in groups_ids:
        interests_by_group_to_AND[group_id] = []
    for interest_input in input_data_json[constants.INPUT_INTEREST_FIELD]:
        if interest_input:
            if constants.GROUP_ID_FIELD in interest_input:
                interest_group_id = interest_input[constants.GROUP_ID_FIELD]
                if interest_group_id in interests_by_group_to_AND:
                    interests_by_group_to_AND[interest_group_id].append(interest_input)
    return interests_by_group_to_AND


def select_advance_targeting_type_array_integer(segment_type, input_value, targeting):
    api_field_name = get_api_field_name(segment_type)
    if input_value:
        if "or" in input_value:
            targeting["flexible_spec"].append({api_field_name: input_value["or"]})
        elif "not" in input_value:
            if not "exclusions" in targeting:
                targeting["exclusions"] = {}
            if not api_field_name in list(targeting["exclusions"].keys()):
                targeting["exclusions"][api_field_name] = []
            for value in input_value["not"]:
                targeting["exclusions"][api_field_name].append(value)
        else:
            raise JsonFormatException("Something wrong with: " + str(input_value))


def select_advance_targeting_fields(targeting, input_combination_dictionary):
    # Selecting Advance Targeting
    targeting["flexible_spec"] = []

    for advance_field in constants.ADVANCE_TARGETING_FIELDS_TYPE_ARRAY_IDS:
        if advance_field in input_combination_dictionary:
            select_advance_targeting_type_array_ids(advance_field, input_combination_dictionary[advance_field],
                                                    targeting)
    for advance_field in constants.ADVANCE_TARGETING_FIELDS_TYPE_ARRAY_INTEGER:
        if advance_field in input_combination_dictionary:
            select_advance_targeting_type_array_integer(advance_field, input_combination_dictionary[advance_field],
                                                        targeting)
    return targeting


def select_publisher_platform(targeting, input_data):
    # Selecting Publisher Platform
    platform = constants.PUBLISHER_PLATFORM_DEFAULT
    if constants.API_PUBLISHER_PLATFORMS_FIELD in input_data:
        platform = input_data[constants.API_PUBLISHER_PLATFORMS_FIELD]
    targeting[constants.API_PUBLISHER_PLATFORMS_FIELD] = platform


def build_targeting(current_combination, input_data):
    targeting = {}
    input_combination_dictionary = dict(current_combination)
    select_common_fields_in_targeting(targeting, input_combination_dictionary)
    select_advance_targeting_fields(targeting, input_combination_dictionary)
    select_publisher_platform(targeting, input_data)
    return targeting


def get_token_and_account_number_or_wait():
    if not "used_tokens_time_map" in globals():
        global used_tokens_time_map
        used_tokens_time_map = {}
    while True:
        for token, account in constants.TOKENS:
            if token in used_tokens_time_map:
                last_used_time = used_tokens_time_map[token]
                time_since_used = time.time() - last_used_time
                if time_since_used > constants.SLEEP_TIME:
                    used_tokens_time_map[token] = time.time()
                    return token, account
            else:
                used_tokens_time_map[token] = time.time()
                return token, account
        time.sleep(1)


def print_collecting_progress(uncomplete_df, df):
    full_size = len(df)
    uncomplete_df_size = len(uncomplete_df)
    print_info(
        "Collecting... Completed: {:.2f}% , {:d}/{:d}".format((float(full_size - uncomplete_df_size) / full_size * 100),
                                                              full_size - uncomplete_df_size, full_size))


def send_dumb_query(token, account, url):
    try:
        row = pd.Series()
        row[constants.TARGETING_FIELD] = constants.DEFAULT_DUMB_TARGETING
        call_request_fb(row, token, account, url)
    except Exception as error:
        print_warning("Token or Account Number Error:")
        print_warning("Token:" + token)
        print_warning("Account:" + account)
        raise error


def from_FB_polygons_to_KML(poly):
    out = ""
    for p in poly:
        out += "<Polygon><outerBoundaryIs><LinearRing><coordinates>"
        for pair in p:
            out += " %s,%s" % (pair["lng"], pair["lat"])
        out += "</coordinates></LinearRing></outerBoundaryIs></Polygon>"
    return out


def double_country_conversion(input):
    mapping = {
        "AD": "Andorra",
        "AE": "United Arab Emirates",
        "AF": "Afghanistan",
        "AG": "Antigua and Barbuda",
        "AL": "Albania",
        "AM": "Armenia",
        "AO": "Angola",
        "AR": "Argentina",
        "AS": "American Samoa",
        "AT": "Austria",
        "AU": "Australia",
        "AW": "Aruba",
        "AZ": "Azerbaijan",
        "BA": "Bosnia and Herzegovina",
        "BB": "Barbados",
        "BD": "Bangladesh",
        "BE": "Belgium",
        "BF": "Burkina Faso",
        "BG": "Bulgaria",
        "BH": "Bahrain",
        "BI": "Burundi",
        "BJ": "Benin",
        "BM": "Bermuda",
        "BN": "Brunei",
        "BO": "Bolivia",
        "BR": "Brazil",
        "BS": "Bahamas",
        "BT": "Bhutan",
        "BW": "Botswana",
        "BY": "Belarus",
        "BZ": "Belize",
        "CA": "Canada",
        "CD": "Congo Dem. Rep.",
        "CF": "Central African Republic",
        "CG": "Congo Rep.",
        "CH": "Switzerland",
        "CI": "Cote d'Ivoire",
        "CK": "Cook Islands",
        "CL": "Chile",
        "CM": "Cameroon",
        "CN": "China",
        "CO": "Colombia",
        "CR": "Costa Rica",
        "CV": "Cape Verde",
        "CW": "Curacao",
        "CY": "Cyprus",
        "CZ": "Czech Republic",
        "DE": "Germany",
        "DJ": "Djibouti",
        "DK": "Denmark",
        "DM": "Dominica",
        "DO": "Dominican Republic",
        "DZ": "Algeria",
        "EC": "Ecuador",
        "EE": "Estonia",
        "EG": "Egypt",
        "EH": "Western Sahara",
        "ER": "Eritrea",
        "ES": "Spain",
        "ET": "Ethiopia",
        "FI": "Finland",
        "FJ": "Fiji",
        "FK": "Falkland Islands",
        "FM": "Micronesia",
        "FO": "Faroe Islands",
        "FR": "France",
        "GA": "Gabon",
        "GB": "United Kingdom",
        "GD": "Grenada",
        "GE": "Georgia",
        "GF": "French Guiana",
        "GG": "Guernsey",
        "GH": "Ghana",
        "GI": "Gibraltar",
        "GL": "Greenland",
        "GM": "Gambia",
        "GN": "Guinea-Bissau",
        "GP": "Guadeloupe",
        "GQ": "Equatorial Guinea",
        "GR": "Greece",
        "GT": "Guatemala",
        "GU": "Guam",
        "GW": "Guinea",
        "GY": "Guyana",
        "HK": "Hong Kong",
        "HN": "Honduras",
        "HR": "Croatia",
        "HT": "Haiti",
        "HU": "Hungary",
        "ID": "Indonesia",
        "IE": "Ireland",
        "IL": "Israel",
        "IM": "Isle of Man",
        "IN": "India",
        "IQ": "Iraq",
        "IR": "Iran",
        "IS": "Iceland",
        "IT": "Italy",
        "JE": "Jersey",
        "JM": "Jamaica",
        "JO": "Jordan",
        "JP": "Japan",
        "KE": "Kenya",
        "KG": "Kyrgyzstan",
        "KH": "Cambodia",
        "KI": "Kiribati",
        "KM": "Comoros",
        "KN": "Saint Kitts and Nevis",
        "KR": "South Korea",
        "KW": "Kuwait",
        "KY": "Cayman Islands",
        "KZ": "Kazakhstan",
        "LA": "Laos",
        "LB": "Lebanon",
        "LC": "Saint Lucia",
        "LI": "Liechtenstein",
        "LK": "Sri Lanka",
        "LR": "Liberia",
        "LS": "Lesotho",
        "LT": "Lithuania",
        "LU": "Luxembourg",
        "LV": "Latvia",
        "LY": "Libya",
        "MA": "Morocco",
        "MC": "Monaco",
        "MD": "Moldova",
        "ME": "Montenegro",
        "MF": "Saint Martin",
        "MG": "Madagascar",
        "MH": "Marshall Islands",
        "MK": "Macedonia",
        "ML": "Mali",
        "MM": "Myanmar",
        "MN": "Mongolia",
        "MO": "Macau",
        "MP": "Northern Mariana Islands",
        "MQ": "Martinique",
        "MR": "Mauritania",
        "MS": "Montserrat",
        "MT": "Malta",
        "MU": "Mauritius",
        "MV": "Maldives",
        "MW": "Malawi",
        "MX": "Mexico",
        "MY": "Malaysia",
        "MZ": "Mozambique",
        "NA": "Namibia",
        "NC": "New Caledonia",
        "NE": "Niger",
        "NF": "Norfolk Island",
        "NG": "Nigeria",
        "NI": "Nicaragua",
        "NL": "Netherlands",
        "NO": "Norway",
        "NP": "Nepal",
        "NR": "Nauru",
        "NU": "Niue",
        "NZ": "New Zealand",
        "OM": "Oman",
        "PA": "Panama",
        "PE": "Peru",
        "PF": "French Polynesia",
        "PG": "Papua New Guinea",
        "PH": "Philippines",
        "PK": "Pakistan",
        "PL": "Poland",
        "PM": "Saint Pierre and Miquelon",
        "PN": "Pitcairn",
        "PR": "Puerto Rico",
        "PS": "Palestine",
        "PT": "Portugal",
        "PW": "Palau",
        "PY": "Paraguay",
        "QA": "Qatar",
        "RE": "Reunion",
        "RO": "Romania",
        "RS": "Serbia",
        "RU": "Russia",
        "RW": "Rwanda",
        "SA": "Saudi Arabia",
        "SB": "Solomon Islands",
        "SC": "Seychelles",
        "SE": "Sweden",
        "SG": "Singapore",
        "SH": "Saint Helena",
        "SI": "Slovenia",
        "SJ": "Svalbard and Jan Mayen",
        "SK": "Slovakia",
        "SL": "Sierra Leone",
        "SM": "San Marino",
        "SN": "Senegal",
        "SO": "Somalia",
        "SR": "Suriname",
        "SS": "South Sudan",
        "ST": "Sao Tome and Principe",
        "SV": "El Salvador",
        "SY": "Syria",
        "SX": "Sint Maarten",
        "SZ": "Swaziland",
        "TC": "Turks and Caicos Islands",
        "TD": "Chad",
        "TG": "Togo",
        "TH": "Thailand",
        "TJ": "Tajikistan",
        "TK": "Tokelau",
        "TL": "Timor-Leste",
        "TM": "Turkmenistan",
        "TN": "Tunisia",
        "TO": "Tonga",
        "TR": "Turkey",
        "TT": "Trinidad and Tobago",
        "TV": "Tuvalu",
        "TW": "Taiwan",
        "TZ": "Tanzania",
        "UA": "Ukraine",
        "UG": "Uganda",
        "US": "United States",
        "UY": "Uruguay",
        "UZ": "Uzbekistan",
        "VC": "Saint Vincent and the Grenadines",
        "VE": "Venezuela",
        "VG": "British Virgin Islands",
        "VI": "US Virgin Islands",
        "VN": "Vietnam",
        "VU": "Vanuatu",
        "WF": "Wallis and Futuna",
        "WS": "Samoa",
        "XK": "Kosovo",
        "YE": "Yemen",
        "YT": "Mayotte",
        "ZA": "South Africa",
        "ZM": "Zambia",
        "ZW": "Zimbabwe",
    }

    if input in mapping:
        return mapping[input]

    inverted = dict(zip(mapping.values(), mapping.keys()))

    if input in inverted:
        return inverted[input]

    return None


def get_all_countries(two_letters_code=True):
    if two_letters_code:
        return ['AD', 'AE', 'AF', 'AG', 'AL', 'AM', 'AO', 'AR', 'AS', 'AT', 'AU', 'AW', 'AZ', 'BA', 'BB', 'BD', 'BE',
                'BF', 'BG', 'BH', 'BI', 'BJ', 'BM', 'BN', 'BO', 'BR', 'BS', 'BT', 'BW', 'BY', 'BZ', 'CA', 'CD', 'CF',
                'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 'CO', 'CR', 'CV', 'CW', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DM',
                'DO', 'DZ', 'EC', 'EE', 'EG', 'EH', 'ER', 'ES', 'ET', 'FI', 'FJ', 'FK', 'FM', 'FO', 'FR', 'GA', 'GB',
                'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 'GT', 'GU', 'GW', 'GY', 'HK',
                'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IQ', 'IS', 'IT', 'JE', 'JM', 'JO', 'JP',
                'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KR', 'KW', 'KY', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS',
                'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MG', 'MH', 'MK', 'ML', 'MM', 'MN', 'MO', 'MP',
                'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 'NC', 'NE', 'NF', 'NG', 'NI', 'NL',
                'NO', 'NP', 'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG', 'PH', 'PK', 'PL', 'PM', 'PN', 'PR', 'PS',
                'PT', 'PW', 'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW', 'SA', 'SB', 'SC', 'SE', 'SG', 'SH', 'SI', 'SJ',
                'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'SS', 'ST', 'SV', 'SX', 'SZ', 'TC', 'TD', 'TG', 'TH', 'TJ',
                'TK', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'US', 'UY', 'UZ', 'VC', 'VE',
                'VG', 'VI', 'VN', 'VU', 'WF', 'WS', 'XK', 'YT', 'ZA', 'ZM', 'ZW']
    else:
        return ['Andorra', 'United Arab Emirates', 'Afghanistan', 'Antigua and Barbuda', 'Albania', 'Armenia', 'Angola',
                'Argentina', 'American Samoa', 'Austria', 'Australia', 'Aruba', 'Azerbaijan', 'Bosnia and Herzegovina',
                'Barbados', 'Bangladesh', 'Belgium', 'Burkina Faso', 'Bulgaria', 'Bahrain', 'Burundi', 'Benin',
                'Bermuda', 'Brunei', 'Bolivia', 'Brazil', 'Bahamas', 'Bhutan', 'Botswana', 'Belarus', 'Belize',
                'Canada', 'Congo Dem. Rep.', 'Central African Republic', 'Congo Rep.', 'Switzerland', "Cote d'Ivoire",
                'Cook Islands', 'Chile', 'Cameroon', 'China', 'Colombia', 'Costa Rica', 'Cape Verde', 'Curacao',
                'Cyprus', 'Czech Republic', 'Germany', 'Djibouti', 'Denmark', 'Dominica', 'Dominican Republic',
                'Algeria', 'Ecuador', 'Estonia', 'Egypt', 'Western Sahara', 'Eritrea', 'Spain', 'Ethiopia', 'Finland',
                'Fiji', 'Falkland Islands', 'Micronesia', 'Faroe Islands', 'France', 'Gabon', 'United Kingdom',
                'Grenada', 'Georgia', 'French Guiana', 'Guernsey', 'Ghana', 'Gibraltar', 'Greenland', 'Gambia',
                'Guinea-Bissau', 'Guadeloupe', 'Equatorial Guinea', 'Greece', 'Guatemala', 'Guam', 'Guinea', 'Guyana',
                'Hong Kong', 'Honduras', 'Croatia', 'Haiti', 'Hungary', 'Indonesia', 'Ireland', 'Israel', 'Isle of Man',
                'India', 'Iraq', 'Iceland', 'Italy', 'Jersey', 'Jamaica', 'Jordan', 'Japan', 'Kenya',
                'Kyrgyzstan', 'Cambodia', 'Kiribati', 'Comoros', 'Saint Kitts and Nevis', 'South Korea', 'Kuwait',
                'Cayman Islands', 'Kazakhstan', 'Laos', 'Lebanon', 'Saint Lucia', 'Liechtenstein', 'Sri Lanka',
                'Liberia', 'Lesotho', 'Lithuania', 'Luxembourg', 'Latvia', 'Libya', 'Morocco', 'Monaco', 'Moldova',
                'Montenegro', 'Saint Martin', 'Madagascar', 'Marshall Islands', 'Macedonia', 'Mali', 'Myanmar',
                'Mongolia', 'Macau', 'Northern Mariana Islands', 'Martinique', 'Mauritania', 'Montserrat', 'Malta',
                'Mauritius', 'Maldives', 'Malawi', 'Mexico', 'Malaysia', 'Mozambique', 'Namibia', 'New Caledonia',
                'Niger', 'Norfolk Island', 'Nigeria', 'Nicaragua', 'Netherlands', 'Norway', 'Nepal', 'Nauru', 'Niue',
                'New Zealand', 'Oman', 'Panama', 'Peru', 'French Polynesia', 'Papua New Guinea', 'Philippines',
                'Pakistan', 'Poland', 'Saint Pierre and Miquelon', 'Pitcairn', 'Puerto Rico', 'Palestine', 'Portugal',
                'Palau', 'Paraguay', 'Qatar', 'Reunion', 'Romania', 'Serbia', 'Russia', 'Rwanda', 'Saudi Arabia',
                'Solomon Islands', 'Seychelles', 'Sweden', 'Singapore', 'Saint Helena', 'Slovenia',
                'Svalbard and Jan Mayen', 'Slovakia', 'Sierra Leone', 'San Marino', 'Senegal', 'Somalia', 'Suriname',
                'South Sudan', 'Sao Tome and Principe', 'El Salvador', 'Sint Maarten', 'Swaziland',
                'Turks and Caicos Islands', 'Chad', 'Togo', 'Thailand', 'Tajikistan', 'Tokelau', 'Timor-Leste',
                'Turkmenistan', 'Tunisia', 'Tonga', 'Turkey', 'Trinidad and Tobago', 'Tuvalu', 'Taiwan', 'Tanzania',
                'Ukraine', 'Uganda', 'United States', 'Uruguay', 'Uzbekistan', 'Saint Vincent and the Grenadines',
                'Venezuela', 'British Virgin Islands', 'US Virgin Islands', 'Vietnam', 'Vanuatu', 'Wallis and Futuna',
                'Samoa', 'Kosovo', 'Mayotte', 'South Africa', 'Zambia', 'Zimbabwe']
