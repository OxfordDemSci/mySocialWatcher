# -*- coding: utf-8 -*-
from .utils import *
import string
import xml.etree.ElementTree as ET

# TODOs:
# Check pySocialWatcher for reindex that is creating a "Unnamed: 0"

class PySocialWatcher:

    def __init__(self, api_version="17.0", sleep_time=0, save_every_x=300, outputname=None, verbose=True):

        constants.REACHESTIMATE_URL = "https://graph.facebook.com/v" + api_version + "/act_{}/delivery_estimate"
        constants.GRAPH_SEARCH_URL = "https://graph.facebook.com/v" + api_version + "/search"
        constants.TARGETING_SEARCH_URL = "https://graph.facebook.com/v" + api_version + "/act_{}/targetingsearch"
        constants.SLEEP_TIME = sleep_time
        constants.SAVE_EVERY = save_every_x
        constants.VERBOSE = verbose

        constants.UNIQUE_TIME_ID = str(time.time()).split(".")[0]

        constants.DATAFRAME_SKELETON_FILE_NAME = "dataframe_skeleton_" + constants.UNIQUE_TIME_ID + ".csv.gz"
        constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME = "dataframe_collecting_" + constants.UNIQUE_TIME_ID + ".csv.gz"
        constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME = "dataframe_collected_finished_" + constants.UNIQUE_TIME_ID + ".csv.gz"
        constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME_WITHOUT_FULL_RESPONSE = "collect_finished_clean" + constants.UNIQUE_TIME_ID + ".csv.gz"

        if outputname:
            constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME = outputname

    @staticmethod
    def load_credentials_direct(token, account_number):
        PySocialWatcher.add_token_and_account_number(token, account_number)

    @staticmethod
    def load_credentials_file(token_file_path):
        with open(token_file_path, "r") as token_file:
            for line in token_file:
                token = line.split(",")[0].strip()
                account_number = line.split(",")[1].strip()
                PySocialWatcher.add_token_and_account_number(token, account_number)

    @staticmethod
    def add_token_and_account_number(token,account_number):
        constants.TOKENS.append((token,account_number))

    @staticmethod
    def get_search_targeting_from_query_dataframe(query):
        token, account_id = get_token_and_account_number_or_wait()
        request_payload = {
            'q': query,
            'access_token': token
        }
        response = send_request(constants.TARGETING_SEARCH_URL.format(account_id), request_payload)
        json_response = load_json_data_from_response(response)
        return pd.DataFrame(json_response["data"])

    @staticmethod
    def get_behavior_dataframe():
        request_payload = {
            'type': 'adTargetingCategory',
            'class': "behaviors",
            'access_token': get_token_and_account_number_or_wait()[0]
        }
        response = send_request(constants.GRAPH_SEARCH_URL, request_payload)
        json_response = load_json_data_from_response(response)
        return pd.DataFrame(json_response["data"])

    @staticmethod
    def get_income_dataframe():
        request_payload = {
            'type': 'adTargetingCategory',
            'class': "income",
            'access_token': get_token_and_account_number_or_wait()[0]
        }
        response = send_request(constants.GRAPH_SEARCH_URL, request_payload)
        json_response = load_json_data_from_response(response)
        return pd.DataFrame(json_response["data"])

    @staticmethod
    def get_interests_given_query(interest_query):
        request_payload = {
            'type': 'adinterest',
            'q': interest_query,
            'access_token': get_token_and_account_number_or_wait()[0]
        }
        response = send_request(constants.GRAPH_SEARCH_URL, request_payload)
        json_response = load_json_data_from_response(response)
        return pd.DataFrame(json_response["data"])

    @staticmethod
    def get_geo_locations_given_query_and_location_type(query, location_types, region_id=None, country_code=None, limit=1000):
        request_payload = {
            'type': 'adgeolocation',
            'location_types': location_types,
            'limit': limit,
            'access_token': get_token_and_account_number_or_wait()[0]
        }

        if query is not None:
            request_payload['q'] = query

        if region_id is not None:
            request_payload["region_id"] = region_id

        if country_code is not None:
            request_payload["country_code"] = country_code

        response = send_request(constants.GRAPH_SEARCH_URL, request_payload)
        json_response = load_json_data_from_response(response)
        return pd.DataFrame(json_response["data"])

    @staticmethod
    def get_KML_given_geolocation(location_type, list_location_codes):
        """

        :param
        location_type: countries, regions, cities, zips, places, custom_locations, geo_markets, electoral_districts, country_groups
        location_code: region code, country two letters acronym, so on.

        Example: location_type = "countries", location_code = ["BR","CL","AT","US","QA"]
        """
        request_payload = {
            'type': 'adgeolocationmeta',
            location_type: [[ list_location_codes ]],
            'show_polygons_and_coordinates': 'true',
            'access_token': get_token_and_account_number_or_wait()[0]
        }
        response = send_request(constants.GRAPH_SEARCH_URL, request_payload)
        json_response = load_json_data_from_response(response)
        df = pd.DataFrame(json_response["data"])
        if df.empty:
            return None

        ans = {"name":[], "kml":[], "key": []}
        for location in df[location_type]:
            ans["name"].append(location["name"])
            ans["key"].append(location["key"])
            if "polygons" in location:
                ans["kml"].append(from_FB_polygons_to_KML(location["polygons"]))
            else:
                ans["kml"].append("Polygons not found.")
        return pd.DataFrame(ans)

    @staticmethod
    def get_KMLs_for_regions_in_country(country_code):
        """

        :param country_code: one single country code (e.g., "BR","CL","AT","US","QA")

        :return:
        """
        locations = PySocialWatcher.get_geo_locations_given_query_and_location_type(None, ["region"],
                                                                                    country_code=country_code)
        print("Obtained %d regions." % (locations.shape[0]))
        if locations.empty:
            return None

        kmls = PySocialWatcher.get_KML_given_geolocation("regions", list(locations["key"].values))
        print("Obtained %d KMLs." % (kmls.shape[0]))

        return pd.merge(locations, kmls, on=["key", "name"])

    @staticmethod
    def get_all_cities_given_country_code(country_code):
        # Get all regions
        regions = PySocialWatcher.get_geo_locations_given_query_and_location_type(None, ["region"],
                                                                                  country_code=country_code)
        regions = regions[regions["country_code"] == country_code]
        dfs = []
        for idx, row in regions.iterrows():
            print("Getting cities for region named '%s' (id = %s)" % (row["name"], row["key"]))
            df = PySocialWatcher.systematically_get_all_cities(country_code=country_code, region_id=row["key"])

            if not df.empty:
                dfs.append(df)

        concated = None if len(dfs) == 0 else pd.concat(dfs).drop_duplicates(subset="key").reset_index(drop=True)

        return concated

    @staticmethod
    def systematically_get_all_cities(country_code=None, region_id=None, prefix=""):
        dfs = []

        for l in string.ascii_lowercase:
            print("Getting cities that start with %s" % (prefix + l))
            try:
                df = PySocialWatcher.get_geo_locations_given_query_and_location_type(prefix + l, ["city"],
                                                                                country_code=country_code,
                                                                                region_id=region_id)
            except FatalException:
                print("ERROR. Restricting search...")
                df = PySocialWatcher.systematically_get_all_cities(country_code=country_code,
                                                                   region_id=region_id,
                                                                   prefix=prefix + l)

            if df is not None and not df.empty:
                df = df[df["type"] == "city"]
                dfs.append(df)

        concated = None if len(dfs) == 0 else pd.concat(dfs).drop_duplicates(subset="key").reset_index(drop=True)

        return concated

    @staticmethod
    def print_search_targeting_from_query_dataframe(query):
        search_dataframe = PySocialWatcher.get_search_targeting_from_query_dataframe(query)
        print_dataframe(search_dataframe)

    @staticmethod
    def print_geo_locations_given_query_and_location_type(query, location_types, region_id=None, country_code=None):
        geo_locations = PySocialWatcher.get_geo_locations_given_query_and_location_type(query, location_types, region_id=region_id, country_code=country_code)
        print_dataframe(geo_locations)

    @staticmethod
    def print_interests_given_query(interest_query):
        interests = PySocialWatcher.get_interests_given_query(interest_query)
        print_dataframe(interests)

    @staticmethod
    def print_behaviors_list():
        behaviors = PySocialWatcher.get_behavior_dataframe()
        print_dataframe(behaviors)

    @staticmethod
    def print_income_list():
        income = PySocialWatcher.get_income_dataframe()
        print_dataframe(income)

    @staticmethod
    def read_json_file(file_path):
        file_ptr = open(file_path, "r")
        json_file_raw = file_ptr.read()
        file_ptr.close()
        try:
            json_data = json.loads(json_file_raw)
        except ValueError as error:
            raise JsonFormatException(error.message)
        return json_data

    @staticmethod
    def build_collection_dataframe(input_data_json, output_dir = ""):
        if constants.VERBOSE:
            print_info("Building Collection Dataframe")
        collection_dataframe = build_initial_collection_dataframe()
        collection_queries = []
        input_combinations = get_all_combinations_from_input(input_data_json)
        print_info("Total API Requests:" + str(len(input_combinations)))
        for index,combination in enumerate(input_combinations):
            if constants.VERBOSE:
                print_info("Completed: {0:.2f}".format(100*index/float(len(input_combinations))))
            collection_queries.append(generate_collection_request_from_combination(combination, input_data_json))
        dataframe = collection_dataframe.append(collection_queries)
        dataframe = add_timestamp(dataframe)
        dataframe = add_published_platforms(dataframe, input_data_json)
        if constants.SAVE_EMPTY:
            dataframe.to_csv(output_dir + constants.DATAFRAME_SKELETON_FILE_NAME)
        save_skeleton_dataframe(dataframe, output_dir)
        return dataframe

    @staticmethod
    def perform_collection_data_on_facebook(collection_dataframe, output_dir="", remove_tmp_files=False):
        # Call each requests builded
        processed_rows_after_saved = 0
        dataframe_with_uncompleted_requests = collection_dataframe[pd.isnull(collection_dataframe["response"])]
        while not dataframe_with_uncompleted_requests.empty:
            print_collecting_progress(dataframe_with_uncompleted_requests, collection_dataframe)
            # Trigger requests
            rows_to_request = dataframe_with_uncompleted_requests.head(len(constants.TOKENS))
            responses_list = trigger_request_process_and_return_response(rows_to_request, constants.REACHESTIMATE_URL)
            # Save response in collection_dataframe
            save_response_in_dataframe(responses_list, collection_dataframe)
            processed_rows_after_saved += len(responses_list)
            # Save a temporary file
            if processed_rows_after_saved >= constants.SAVE_EVERY:
                save_temporary_dataframe(collection_dataframe, output_dir)
                processed_rows_after_saved = 0
            # Update not_completed_experiments
            dataframe_with_uncompleted_requests = collection_dataframe[pd.isnull(collection_dataframe["response"])]
        print_info("Data Collection Complete")
        save_temporary_dataframe(collection_dataframe, output_dir)
        post_process_collection(collection_dataframe)
        save_after_collecting_dataframe(collection_dataframe, output_dir)

        if remove_tmp_files:
            remove_temporary_dataframes(output_dir)

        return collection_dataframe

    @staticmethod
    def check_tokens_account_valid():
        print_info("Testing tokens and account number")
        for token, account in constants.TOKENS:
            send_dumb_query(token, account, constants.REACHESTIMATE_URL)
        print_info("All tokens and respective account number are valid.")

    @staticmethod
    def check_input_integrity(input_data_json):
        # Check input has name propertity
        if not constants.INPUT_NAME_FIELD in input_data_json:
            raise FatalException("Input should have key: " + constants.INPUT_NAME_FIELD)
        # Check if every field in input is supported
        for field in list(input_data_json.keys()):
            if not field in constants.ALLOWED_FIELDS_IN_INPUT:
                raise FatalException("Field not supported: " + field)

    @staticmethod
    def expand_input_if_requested(input_data_json):
        if constants.PERFORM_AND_BETWEEN_GROUPS_INPUT_FIELD in input_data_json:
            for groups_ids in input_data_json[constants.PERFORM_AND_BETWEEN_GROUPS_INPUT_FIELD]:
                interests_by_group_to_AND = get_interests_by_group_to_AND(input_data_json,groups_ids)
                list_of_ANDS_between_groups = list(itertools.product(*list(interests_by_group_to_AND.values())))
                add_list_of_ANDS_to_input(list_of_ANDS_between_groups, input_data_json)

    @staticmethod
    def run_data_collection(json_input_file_path, output_dir = "", remove_tmp_files=False):
        input_data_json = PySocialWatcher.read_json_file(json_input_file_path)
        PySocialWatcher.expand_input_if_requested(input_data_json)
        PySocialWatcher.check_input_integrity(input_data_json)
        collection_dataframe = PySocialWatcher.build_collection_dataframe(input_data_json, output_dir)
        collection_dataframe = PySocialWatcher.perform_collection_data_on_facebook(collection_dataframe, output_dir, remove_tmp_files)
        return collection_dataframe

    @staticmethod
    def load_data_and_continue_collection(input_file_path, output_dir="", remove_tmp_files=False):
        collection_dataframe = load_dataframe_from_file(input_file_path)
        collection_dataframe = PySocialWatcher.perform_collection_data_on_facebook(collection_dataframe, output_dir, remove_tmp_files)
        return collection_dataframe

    @staticmethod
    def __df_to_geojson(row):
        out = {}

        out["type"] = "Feature"
        if "country" in row:
            out["country"] = row["country"]
            out["id"] = row["name"] + ", " + row["country"]
        else:
            out["id"] = row["name"]

        out["properties"] = {"name": row["name"]}
        if "key" in row:
            out["properties"]["key"] = row["key"]
        if "country" in row:
            out["properties"]["country"] = row["country"]

        skml = row["kml"]

        xml_kml = ET.fromstring("<root>" + skml + "</root>")
        coordinates = xml_kml.findall(".//coordinates")

        list_of_coords = []
        for c in coordinates:
            s = c.text
            coor = []
            for pair in s.split():
                a, b = map(float, pair.split(","))
                coor.append([a, b])
            list_of_coords.append(coor)

        polygon = {"type": "Polygon", "coordinates": list_of_coords}
        out["geometry"] = polygon
        return out

    @staticmethod
    def transform_KML_into_geojson(df, outputname):
        df["country"] = df["country_code"].apply(double_country_conversion)
        features = list(df.apply(lambda x: PySocialWatcher.__df_to_geojson(x), axis=1))
        output = {"type": "FeatureCollection", "features": features}
        with open(outputname, "w") as f:
            json_string = json.dumps(output)
            f.write(json_string)

    @staticmethod
    def print_bad_joke():
        print("I used to think the brain was the most important organ.\nThen I thought, look what’s telling me that.")
