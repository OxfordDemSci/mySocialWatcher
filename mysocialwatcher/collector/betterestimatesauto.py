import pandas as pd
import sys
import os
import ast
import json
from pysocialwatcher import watcherAPI
from pysocialwatcher import constants

import pickle
import datetime

# To avoid warnings from old python installation
import requests
import time
requests.packages.urllib3.disable_warnings()

## Parameters
# Should we stop re-issuing a query once we found a better estimate for it?
single_estimation = True
max_try = 2 # how many times to keep trying if we fail midway ## change to 2
time_wait = 0 # waits 5 minutes between tries

#infile = sys.argv[1]
#credentials_file = sys.argv[2]

#countries_to_try = ["US","CA"]

countries_to_try = ["AD","AE","AF","AG","AI","AL","AM","AO","AR","AS","AT","AU","AW","AZ","BA","BB",
                    "BD","BE","BF","BG","BH","BI","BJ","BL","BM","BN","BO","BQ","BR","BS","BT","BW","BY","BZ",
                    "CA","CD","CF","CG","CH","CI","CK","CL","CM","CN","CO","CR","CV","CW","CY","CZ","DE",
                    "DJ","DK","DM","DO","DZ","EC","EE","EG","ER","ES","ET","FI","FJ","FK","FM","FO","FR","GA",
                    "GB","GD","GE","GF","GG","GH","GI","GL","GM","GN","GP","GQ","GR","GT","GU","GW","GY","HK",
                    "HN","HR","HT","HU","ID","IE","IL","IM","IN","IQ","IS","IT","JE","JM","JO","JP","KE",
                    "KG","KH","KI","KM","KN","KR","KW","KY","KZ","LA","LB","LC","LI","LK","LR","LS","LT","LU","LV",
                    "LY","MA","MC","MD","ME","MF","MG","MH","MK","ML","MM","MN","MO","MP","MQ","MR","MS","MT","MU",
                    "MV","MW","MX","MY","MZ","NA","NC","NE","NG","NI","NL","NO","NP","NR","NZ","OM","PA",
                    "PE","PF","PG","PH","PK","PL","PM","PR","PS","PT","PW","PY","QA","RE","RO","RS","RW",
                    "SA","SB","SC","SE","SG","SH","SI","SJ","SK","SL","SM","SN","SO","SR","SS","ST","SV","SX","SZ",
                    "TC","TD","TG","TH","TJ","TL","TM","TN","TO","TR","TT","TV","TW","TZ",
                    "UA","UG","US","UY","UZ","VC","VE","VG","VI","VN","VU","WF","WS","XK",
                    "YE","YT","ZA","ZM","ZW"]

##
constants.SLEEP_TIME = 0
constants.SAVE_EVERY = 1000

constants.REACHESTIMATE_URL = "https://graph.facebook.com/v17.0/act_{}/delivery_estimate"
constants.GRAPH_SEARCH_URL = "https://graph.facebook.com/v17.0/search"
constants.TARGETING_SEARCH_URL = "https://graph.facebook.com/v17.0/act_{}/targetingsearch"


## Helper functions

def prepare_to_reissue(df):
    df["response"] = None


"""
TODO: Proably the best way is to copy the dictionary 'row' and return a new object.
"""


def replace_by_country(row, country="BR"):
    for option in ["countries", "regions", "cities", "custom_locations","neighborhoods","zips"]:
        if option in row["geo_locations"]:
            del row["geo_locations"][option]
    row["geo_locations"]["countries"] = [country]
    return row


def add_country(row, country="BR"):
    if "countries" in row["geo_locations"]:
        countries = row["geo_locations"]["countries"]
        if country not in countries:
            countries.append(country)
    else:
        countries = [country]

    row["geo_locations"]["countries"] = countries
    return row


def check_country_overlap(row, country="BR"):
    if "countries" in row["geo_locations"]:
        countries = row["geo_locations"]["countries"]
        if country in countries:
            return True
        else:
            return False
    else:
        return False
    


def check_overlap(row, country="BR"):
    """
    Check overlap between a geolocation and the country we are using for estimation.
    Note that in order for this to work, when collecting data, include a key called
    'country_code' in the geo_locations in the config json file. this key should 
    be a list with country codes that overlap with that location.
    """
    
    country_in_location_field = set([])
    country_in_country_field = set([country])
    
    if "country_code" in row:
        for c in row["country_code"]:
            country_in_location_field.add(c)
    
    # The same country was found in the list of countries and list of cities. Flag an error.
    if len(country_in_location_field.intersection(country_in_country_field)) > 0:
        return True

    # if everything is okay, there is no overlap
    return False


def save_partial_results(df, list_estimates_lower, list_estimates_upper, infile):
    res_lower = pd.DataFrame(list_estimates_lower).T
    result_lower = res_lower.mean(axis=1)
    
    res_upper = pd.DataFrame(list_estimates_upper).T
    result_upper = res_upper.mean(axis=1)

    # These are the queries that we can safely replace in the input dataset
    df.loc[result_lower.index, constants.MAU_LOWER_AUDIENCE_FIELD] = result_lower
    df.loc[result_upper.index, constants.MAU_UPPER_AUDIENCE_FIELD] = result_upper
    
    savefile = "%s.betterestimate" % (infile)
    df.to_csv(savefile + ".gz", compression='gzip', index=False)

    found_better_estimate_lower = (result_lower < 1000).sum()
    still_can_get_better_estimates_lower = df[constants.MAU_LOWER_AUDIENCE_FIELD].isnull().sum()
    found_better_estimate_upper = (result_upper < 1000).sum()
    still_can_get_better_estimates_upper = df[constants.MAU_UPPER_AUDIENCE_FIELD].isnull().sum()

    print("Saved better estimates for %d lower and %d upper queries in file '%s'..." % (found_better_estimate_lower, found_better_estimate_upper, savefile + ".gz"))
    print("Still missing to find better estimatives to %d (%.3f) lower and %d (%.3f) upper queries..." % (
    still_can_get_better_estimates_lower, 1. * (still_can_get_better_estimates_lower) / df.shape[0],
    still_can_get_better_estimates_upper, 1. * (still_can_get_better_estimates_upper) / df.shape[0]))
    print("Saved partial results to file '%s'" % (savefile + ".gz"))
    return (result_lower, result_upper)


def is_bad_country(key, country):
    countries = str_to_set(r.get(key))
    if countries is None:
        return False
    if country in countries:
        return True
    return False


def append_redis(key, country):
    countries = str_to_set(r.get(key))
    if not countries:
        countries = set([])
    countries.add(country)
    # print("Adding key: ", key, " - countries:", set_to_str(countries))
    return r.set(key, set_to_str(countries), expiration_in_sec)


def clean_cache(key):
    r.set(key, "")


def set_to_str(s):
    if s:
        return "_".join(s)


def str_to_set(s):
    if s:
        return set(s.split("_"))


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

def perform_collection(df):
    numtry = 0
    data_collection_incomplete = True
    while numtry < max_try and data_collection_incomplete:
        numtry = numtry + 1
        try:
            res = watcherAPI.perform_collection_data_on_facebook(df)
            data_collection_incomplete = False

        except Exception as err:
            # We get an error when we OR a region and a country if the region is inside the country.
            # e.g., region = doha, country = QA -> Error: Some of your locations overlap. Try removing a location.
            # We just ignore this country in our estimates
            if (numtry < max_try):
                print("Found the following error: {0}".format(err))
                print("Have ", max_try - numtry, "tries left. Will keep trying again after ", time_wait, " seconds.")
                time.sleep(time_wait)
    if not data_collection_incomplete:
        print("Collection completed! Attempting rerun if necessary!")
        df = rerun_collection(df)
    return(df)


# function to make rerun attempts
def rerun_collection(df):
    not_estimate_ready = r'estimate_ready":false'
    idx_not_ready = (df[constants.RESPONSE_FIELD].astype(str).str.contains(not_estimate_ready))
    if sum(idx_not_ready) == 0:
        print("All queries are estimate ready. Will not rerun.")
        return(df)
    
    # will need to rerun the data collection
    print("Number of queries that are not estimate ready:",sum(idx_not_ready))
    print("Will re-run the data collection for entries that are not estimate ready.")
    df.loc[idx_not_ready, constants.RESPONSE_FIELD] = None
    
    rerun_number = 0
    while True:
        print("Starting rerun number: ",rerun_number)
        
        try:
            df = watcherAPI.perform_collection_data_on_facebook(df)
        except Exception as err:
            print("Found the following error: {0}".format(err))
            print("Will keep trying again after ", time_wait, " seconds.")
            time.sleep(time_wait)
            continue
        
        rerun_number = rerun_number + 1
        idx_not_ready = (df[constants.RESPONSE_FIELD].astype(str).str.contains(not_estimate_ready))
        if sum(idx_not_ready) == 0:
            break
        else:
            df.loc[idx_not_ready, constants.RESPONSE_FIELD] = None
            print("Some estimates are still not ready.")
            print("Collection will be rerun again in" + str(time_wait) + "seconds")
            time.sleep(time_wait)
    print("Rerun completed!")
    return(df)

def setup_cache(cacheFolder, cacheFileName):
    curr_dir = os.getcwd()
    os.chdir(cacheFolder)
    if os.path.exists(cacheFileName):
        cacheDict = pickle.load(open(cacheFileName, "rb" ))
    else:
        cacheDict = dict()
        cacheDict['date_created'] = datetime.datetime.now()
    os.chdir(curr_dir)

    return(cacheDict)

def get_query_set_from_fields(query_fields):
    query_set = set()
    #print(query_fields)
    #print(type(query_fields))
    for idx, qt in enumerate(query_fields):
        #print('id:' + str(idx) + 'query:' + str(qt))
        field_name = qt[0]
        field_spec = qt[1]
        if (field_name != 'geo_locations') & (field_spec is not None):
            query = str(qt)  # convert to string so we can put in a set
            query_set.add(query)

    query_set = frozenset(query_set)

    return(query_set)
def is_query_invald_for_country(cacheDict, query_fields, country):
    query_set = get_query_set_from_fields(query_fields)
    if query_set in cacheDict:
        countries = cacheDict[query_set]
    else:
        countries = set()

    return (country in countries)

def append_to_cache(cacheDict, query_fields, country):
    query_set = get_query_set_from_fields(query_fields)
    if query_set in cacheDict:
        cacheDict[query_set].add(country)
    else:
        cacheDict[query_set] = set([country])

def save_cache(cacheDict, cacheFolder, cacheFileName):
    curr_dir = os.getcwd()
    os.chdir(cacheFolder)
    pickle.dump(cacheDict,open(cacheFileName,'wb'))
    os.chdir(curr_dir)

    print("Cached saved to folder:" + cacheFolder)

##
def estimate_sparse_queries(infile, credentials_file=None, usingCache=True, cacheFolder='.', cacheFileName = 'sparsity_estimation_cache.p'):

    if usingCache:
        # setting up the cache
        cacheDict = setup_cache(cacheFolder, cacheFileName)
        print("Using cache to avoid unfruitful API calls")

    # read in the file or an existing version with partially done betterestimation
    partial_file = "%s.betterestimate.gz" % (infile)
    if os.path.exists(partial_file):
        print("Found partially completed betterestimation from a previous round. Will continue from that.")
        print(partial_file)
        df = pd.read_csv(partial_file)
    else:
        df = pd.read_csv(infile)
    
    # if there are no sparse queries don't run anything
    if df[constants.MAU_UPPER_AUDIENCE_FIELD].isnull().sum() == 0:
        queries_need_better_estimate = df[(df[constants.MAU_UPPER_AUDIENCE_FIELD] == 1000)].shape[0]
        if queries_need_better_estimate == 0:
            # there are no sparse queries, no API calls to be made
            print("There are no queries with an audience size of 1000. Nothing to be done here!")
            return 0 
    
    watcher = watcherAPI()
   # watcher.config(sleep_time=0, save_every=1000)
    # if called from within another script already using watcherAPI the credentials will already be loaded
    if credentials_file is not None: 
        watcher.load_credentials_file(credentials_file)

    constants_DATAFRAME_SKELETON_FILE_NAME = constants.DATAFRAME_SKELETON_FILE_NAME
    constants_DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME = constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME
    constants_DATAFRAME_AFTER_COLLECTION_FILE_NAME = constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME

    #result = None
    result_lower = None
    result_upper = None
    list_estimates_upper = []
    list_estimates_lower = []
    valid_estimate_upper = []  # checks if a new estimate is in between 1001 and 9999.
    valid_estimate_lower = []
    
    total_queries = df.shape[0]
    if df[constants.MAU_UPPER_AUDIENCE_FIELD].isnull().sum() > 0:
        print("Found at least an NAN value for mau_audience...will try to find better estimates only for NAN")
        queries_need_better_estimate = df[(df[constants.MAU_UPPER_AUDIENCE_FIELD].isnull())].shape[0]
        TACKLE_NAN = True

        print("%d (%.3f) rows in the input file have an NaN estimation. Trying to find better estimates for those using the following countries (%s)" %
                    (queries_need_better_estimate, 1.0 * queries_need_better_estimate / total_queries, countries_to_try))
    else:
        queries_need_better_estimate = df[(df[constants.MAU_UPPER_AUDIENCE_FIELD] == 1000)].shape[0]
        TACKLE_NAN = False

        print("%d (%.3f) rows in the input file have an estimated audience of 1000 people. Trying to find better estimates for those using the following countries (%s)" %
                    (queries_need_better_estimate, 1.0 * queries_need_better_estimate / total_queries, countries_to_try))

    # Transform str into JSON -- BAD approach. The set will be later modified and will impact in the original df. Alternatively, I could save it and get it back at the end.
    # df["targeting"] = df["targeting"].apply(lambda x: x))
    totalAPIcalls = 0
    for country in countries_to_try:
        print ("USING COUNTRY: ", country)
        print("Starting Time:" + str(datetime.datetime.now()))
        
        if TACKLE_NAN:
            df1000 = df[df[constants.MAU_UPPER_AUDIENCE_FIELD].isnull()].copy()
        else:
            df1000 = df[df[constants.MAU_UPPER_AUDIENCE_FIELD] == 1000].copy()

        df1000["exploring"] = True
        valid = pd.Series(False, index=df1000.index)

        if single_estimation:
            # In this case, we should avoid re-issueing queries that we have a valid estimate
            if len(valid_estimate_upper) > 0:
                tmpvalid = pd.DataFrame(valid_estimate_upper).T
                tmpvalid = tmpvalid.any(axis=1)
                # Issues only the queries that we do not have info yet
                # df1000 = df1000[~tmpvalid]
                df1000.loc[tmpvalid, "exploring"] = False

        # if using the cache, we need the tupled version to be able to save a string in redis
        df1000["tupled"] = df1000["targeting"].apply(lambda x: str(ordered(ast.literal_eval(x))))
        df1000["tupled_country"] = df1000["targeting"].apply(
            lambda x: str(ordered(replace_by_country(ast.literal_eval(x), country))))

        if usingCache:
            print("Checking API calls in the cache system...")
            # Only keep the rows that we have never explored
            print("Before checking cache: %d queries could have been made." % (df1000["exploring"].sum()))
            df1000.loc[df1000[constants.ALLFIELDS_FIELD].apply(
                lambda x: is_query_invald_for_country(cacheDict, ast.literal_eval(x), country)), "exploring"] = False
            print("After checking cache: %d queries will be made." % (df1000["exploring"].sum()))
            print("Computing Queries...")
        
        # Remove locations that are countries and the same as the country we are using for estimation
        print("Before checking for country overlap %d queries will be made." % (df1000["exploring"].sum()))
        df1000.loc[df1000["targeting"].apply(
            lambda x: check_country_overlap(ast.literal_eval(x), country)), "exploring"] = False
        print("After checking for country overlap: %d queries will be made." % (df1000["exploring"].sum()))
        
        df1000_in_country = df1000.copy(deep=True)
        df1000_add_country = df1000.copy(deep=True)

        # Modifies "targeting" to include country
        df1000_add_country["targeting"] = df1000_add_country["targeting"].apply(
            lambda x: add_country(ast.literal_eval(x), country))
        df1000_in_country["targeting"] = df1000_in_country["targeting"].apply(
            lambda x: replace_by_country(ast.literal_eval(x), country))

        # Check if region is inside country. If it is, return None
        df1000_add_country.loc[df1000_add_country["geo_locations"].apply(
            lambda x: check_overlap(ast.literal_eval(x), country)), "targeting"] = None
        print("After checking for location overlap: %d queries were removed." % (df1000_add_country["targeting"].isnull().sum()))
        
        # Remove rows which targeting is invalid.
        df1000_add_country.loc[
            (df1000_add_country["targeting"].isnull()) | (df1000_in_country["targeting"].isnull()), "exploring"] = False
        df1000_in_country.loc[
            (df1000_add_country["targeting"].isnull()) | (df1000_in_country["targeting"].isnull()), "exploring"] = False

        try:
            # Mark all API calls that are explorable to have response = Null -> this is required by pySocialWatcher.
            print("First part. We should make %d API queries." % (df1000_in_country["exploring"].sum()))
            queries_to_run = dict()
            for idx, row in df1000_in_country.iterrows():
                exploring = df1000_in_country.loc[idx, "exploring"]
                query = df1000_in_country.loc[idx, "tupled_country"]
                if exploring:
                    if query not in queries_to_run:
                        queries_to_run[query] = idx
                        df1000_in_country.loc[idx, "response"] = None
            # df1000_add_country.loc[df1000_add_country["exploring"], "response"] = None
            print("But, we are actually making %d API queries." % (df1000_in_country["response"].isnull().sum()))
            totalAPIcalls = totalAPIcalls + df1000_in_country["response"].isnull().sum()
            #print("queries being explored:")
            #print(df1000_in_country.loc[df1000_in_country["response"].isnull(),constants.ALLFIELDS_FIELD])
            
            # This is the case in which we do not have any new query to issue. Just continue to the next country
            if df1000_in_country["response"].isnull().sum() == 0:
                print("No queries to issue for this country...")
                continue
            #df1000_in_country.to_csv('df1000_in_country.csv', index = False)
            
            perform_collection(df1000_in_country)

            # if the data collection failed to be completed skip this country
            if df1000_in_country["response"].isnull().sum() != 0:
                print("Failed to collect data for this country...")
                print("Carrying on with the next country")
                continue
            
            
            # fill in the values for the duplicate queries
            for idx, row in df1000_in_country.iterrows():
                exploring = df1000_in_country.loc[idx, "exploring"]
                query = df1000_in_country.loc[idx, "tupled_country"]
                if exploring:
                    j = queries_to_run[query]
                    response = df1000_in_country.loc[j, "response"]
                    df1000_in_country.loc[idx,"response"] = response
            watcher.perform_collection_data_on_facebook(df1000_in_country) # to record the mau and dau values

            print("-----------------------------------------------------")
            print("for Country: %s, we have the following results:" % country)
            print("Num. valid queries: %d" % sum((df1000_in_country["exploring"]) &
                                                 (1000 < df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD]) & 
                                                 (df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] < 10000) &
                                                 (1000 < df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD]) & 
                                                 (df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] < 10000)))
            print("Num. Invalid queries (too big: > 10K): %d" % sum((df1000_in_country["exploring"]) & 
                                                ((df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] >= 10000) |
                                                (df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] >= 10000))))
            print("Num. Invalid queries (too sparse: == 1K): %d" % sum((df1000_in_country["exploring"]) & 
                                                ((df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] <= 1000) | 
                                                (df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] <= 1000))))
            invalid = sum((df1000_in_country["exploring"]) & ((df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] >= 10000) |
                                                (df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] >= 10000) | (df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] <= 1000) | (
                                                df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] <= 1000)))
            invalid = invalid/(df1000_in_country["exploring"].sum()) * 100
            print("Perc. Invalid queries: %d perc." % invalid)
            print(" *** ")
            print("Second part. We should make %d API queries." % (df1000_add_country["exploring"].sum()))

            # We can save API call by not exploration queries that we are invalid
            df1000_add_country.loc[((df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] >= 10000) |
                                                (df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] >= 10000) | (df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] <= 1000) | (
                                                df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] <= 1000)), "exploring"] = False
            df1000_add_country.loc[df1000_add_country["exploring"], "response"] = None

            print("But, we are actually making %d API queries." % (df1000_add_country["exploring"].sum()))
            totalAPIcalls = totalAPIcalls + df1000_add_country["exploring"].sum()
            #df1000_add_country.to_csv('df1000_add_country.csv', index = False)
            
            # Explore the remaining queries
            perform_collection(df1000_add_country)
            if df1000_add_country["response"].isnull().sum() != 0:
                print("Failed to collect data for this country...")
                print("Carrying on with the next country")
                continue
        except Exception as err:
            # We get an error when we OR a region and a country if the region is inside the country.
            # e.g., region = doha, country = QA -> Error: Some of your locations overlap. Try removing a location.
            # We just ignore this country in our estimates
            print("Found the following error: {0}".format(err))
            print("Ignoring country %s and continuing..." % (country))
            continue

        # We first check if these estimates are good... Both datasets need to have more than 1000 and less than 10000
        v = (df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] > 1000) & (df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] < 10000) & \
            (df1000_add_country[constants.MAU_UPPER_AUDIENCE_FIELD] > 1000) & (df1000_add_country[constants.MAU_UPPER_AUDIENCE_FIELD] < 10000) & \
            (df1000_add_country[constants.MAU_UPPER_AUDIENCE_FIELD] >= df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD]) & \
            (df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] > 1000) & (df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] < 10000) & \
            (df1000_add_country[constants.MAU_LOWER_AUDIENCE_FIELD] > 1000) & (df1000_add_country[constants.MAU_LOWER_AUDIENCE_FIELD] < 10000) & \
            (df1000_add_country[constants.MAU_LOWER_AUDIENCE_FIELD] >= df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD])

        # Updates the series keeping the correct indices (sync'ed with df1000)
        valid.update(v)

        valid_estimate_upper.append(valid)
        valid_estimate_lower.append(valid)
        
        v_in_country = (df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] > 1000) & (df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] < 10000) & \
        (df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] > 1000) & (df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] < 10000)

        estimates_upper = df1000_add_country[constants.MAU_UPPER_AUDIENCE_FIELD] - df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD]
        estimates_upper.loc[~valid] = None
        estimates_upper.name = country

        estimates_lower = df1000_add_country[constants.MAU_LOWER_AUDIENCE_FIELD] - df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD]
        estimates_lower.loc[~valid] = None
        estimates_lower.name = country

        list_estimates_upper.append(estimates_upper)
        list_estimates_lower.append(estimates_lower)

        print("Finished collection for %s. Saving partial results." % (country))
        # Save the results given the current list of estimates
        #result = save_partial_results(df, list_estimates, infile + "_" + country + "_")
        result_lower, result_upper = save_partial_results(df, list_estimates_lower, list_estimates_upper, infile)

        # For the next country, we need to change our policy to tackle None's instead of 1000's
        TACKLE_NAN = True

        if usingCache:
            print("Updating the Cache.")
            v_in_country = (df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] > 1000) & \
            (df1000_in_country[constants.MAU_LOWER_AUDIENCE_FIELD] < 10000) & \
            (df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] > 1000) & \
            (df1000_in_country[constants.MAU_UPPER_AUDIENCE_FIELD] < 10000)
            bad_queries = df1000_in_country[~v_in_country]
            bad_queries[constants.ALLFIELDS_FIELD].drop_duplicates().apply(
                lambda x: append_to_cache(cacheDict, ast.literal_eval(x), country))
            save_cache(cacheDict, cacheFolder, cacheFileName)

        # save the in-country data frame for later inspection
        # savefile = country + "_df.csv"
        # df1000_in_country.to_csv(savefile + ".gz", compression='gzip', index=False)

    # df1000_in_country.to_csv(country + "_df1000_in_country.csv")
    # df1000_add_country.to_csv(country + "_df1000_add_country.csv")

    # We say we got a valid estimate for a row if any auxiliary estimate is valid
    valid_lower = pd.DataFrame(valid_estimate_lower).T
    valid_lower = valid_lower.any(axis=1)
    valid_upper = pd.DataFrame(valid_estimate_upper).T
    valid_upper = valid_upper.any(axis=1)

    if result_lower is None:
        print("ERROR LOWER: could not run for the selected countries.")
        return totalAPIcalls
        #sys.exit(1)
    if result_upper is None:
        print("ERROR UPPER: could not run for the selected countries.")
        return totalAPIcalls
        #sys.exit(1)

    if result_lower.shape[0] != queries_need_better_estimate:
        print("WARNING: We could not find LOWER estimators for all the regions. Try increasing the number of countries used as input. Currently using %s" % (
                countries_to_try))
    if result_upper.shape[0] != queries_need_better_estimate:
        print("WARNING: We could not find UPPER estimators for all the regions. Try increasing the number of countries used as input. Currently using %s" % (
                countries_to_try))

    still_can_get_better_estimates_lower = df[constants.MAU_LOWER_AUDIENCE_FIELD].isnull().sum()
    still_can_get_better_estimates_upper = df[constants.MAU_UPPER_AUDIENCE_FIELD].isnull().sum()

    print("Found better estimates to %d lower and %d upper queries." % (df[df[constants.MAU_LOWER_AUDIENCE_FIELD] < 1000].shape[0], df[df[constants.MAU_UPPER_AUDIENCE_FIELD] < 1000].shape[0]))
    print("Still missing to find better estimates to %d (%.3f) lower and %d (%.3f) upper queries..." % (still_can_get_better_estimates_lower, \
                                                                                1. * (still_can_get_better_estimates_lower/df.shape[0]), \
                                                                                still_can_get_better_estimates_upper, \
                                                                                1. * (still_can_get_better_estimates_upper/df.shape[0])))

    #save_partial_results(df, result, infile)

    print("All Done.")

    if os.path.exists(constants.DATAFRAME_SKELETON_FILE_NAME):
        os.remove(constants.DATAFRAME_SKELETON_FILE_NAME)
    if os.path.exists(constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME):
        os.remove(constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME)
    if os.path.exists(constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME):
        os.remove(constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME)

    # reset the file names to their original names
    constants.DATAFRAME_SKELETON_FILE_NAME = constants_DATAFRAME_SKELETON_FILE_NAME
    constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME = constants_DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME
    constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME = constants_DATAFRAME_AFTER_COLLECTION_FILE_NAME

    return totalAPIcalls

# Provide two arguments in the command line
# 1st is the data collection file name
# 2nd is the credentials file
if __name__ == "__main__":
    infile  = sys.argv[1]
    credentials_file = sys.argv[2]

    estimate_sparse_queries(infile, credentials_file)
