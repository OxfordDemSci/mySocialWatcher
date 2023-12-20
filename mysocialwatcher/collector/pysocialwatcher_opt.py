"""

Description: Implements optimized data collection methods for the pySocialWatcher
    library, to reduce volume of unfruitful API calls for sparse queries.

Notes:
    O Incomplete DAU estimates: If you decide to use these methods, API calls
      may never be issued for some sparse queries. As a result DAU estimates
      will not be available for some queries. In such cases the DAU estimate is
      indicated by value of -1.
    O Retrying for sparse queries: Since the FB API can sometimes erroneously return sparse
      values, you may want to double check the values of these queries. To do so, set the
      NUMBER_OF_RETRIES_ON_SPARSE_QUERIES parameter to indicate how many times you want
      to re-run the collection for queries with sparse values to make sure they are
      correct. Set SLEEP_TIMES_BETWEEN_RETRIES parameter to indicate sleep time in hours
      between subsequent retries.

Updates:
[11 Aug 2019]: updated to retry on failed FB queries.
"""

# import libraries
from pysocialwatcher import watcherAPI
from pysocialwatcher.utils import load_dataframe_from_file
from pysocialwatcher import constants
import itertools
import pandas as pd
import time
from numpy import isnan
import mysocialwatcher.collector.params
import copy

# -------------------------------------------------------------------------

class pysocialwatcher_opt(watcherAPI):

    def __init__(self, api_version="17.0", sleep_time=12, save_every_x=300, outputname=None):

        constants.REACHESTIMATE_URL = "https://graph.facebook.com/v" + api_version + "/act_{}/delivery_estimate"
        constants.GRAPH_SEARCH_URL = "https://graph.facebook.com/v" + api_version + "/search"
        constants.TARGETING_SEARCH_URL = "https://graph.facebook.com/v" + api_version + "/act_{}/targetingsearch"
        constants.SLEEP_TIME = sleep_time
        constants.SAVE_EVERY = save_every_x

        constants.UNIQUE_TIME_ID = str(time.time()).split(".")[0]

    """
        Given pysocialwatcher's collection dataframe as input, it extracts
        the targeting fields and their specs. It also indexes each query
        in the dataframe by its set of targeting criteria.
    """
    @staticmethod
    def get_query_fields_and_contents(collection_dataframe):
        query_fields = set() # the specified fields
        query_field_specs = dict() # values of each field
        query_indices = dict() # index of each query in dataframe

        # Get the field value for all ages/all genders
        age_field = constants.INPUT_AGE_RANGE_FIELD
        all_age_value = pysocialwatcher_opt.find_overall_age_group(collection_dataframe)['all_ages_value']

        gender_field = constants.INPUT_GENDER_FIELD
        all_gender_value = params.ALL_GENDERS_VALUE

        col_name = constants.ALLFIELDS_FIELD
        for index, row in collection_dataframe.iterrows():
            # parse the fields specified in this query
            query_tup = row[col_name]
            query_set = set()
            for idx, qt in enumerate(query_tup):
                field_name = qt[0]
                field_spec = qt[1]
                query_fields.add(field_name)
                if field_name not in query_field_specs.keys():
                    query_field_specs[field_name] = set()

                # For the overall age/gender group we leave it as unspecified
                if all_age_value is not None:
                    if (field_name == age_field) and (field_spec == all_age_value):
                        field_spec = None
                if (field_name == gender_field) and (field_spec == all_gender_value):
                    field_spec = None

                if field_spec is not None:
                    query = str(qt)  # convert to string so we can put in a set
                    query_field_specs[field_name].add(query)
                    query_set.add(query)

            # index the query location in the dataframe
            query_set = frozenset(query_set)
            query_indices[query_set] = index

        # eliminate fields that are empty as no disaggregation is made by those fields
        all_fields = [field_name for field_name in query_fields]
        for field_name in all_fields:
            if len(query_field_specs[field_name]) == 0:
                query_field_specs.pop(field_name)
                query_fields.remove(field_name)

        return query_fields, query_field_specs, query_indices

    @staticmethod
    def find_overall_age_group(collection_dataframe):
        col_name = constants.ALLFIELDS_FIELD
        age_col =  constants.INPUT_AGE_RANGE_FIELD
        age_values = []
        for index, row in collection_dataframe.iterrows():
            # parse the fields specified in this query
            query_tup = row[col_name]
            for idx, qt in enumerate(query_tup):
                #print(index, idx, qt)
                field_name = qt[0]
                field_spec = qt[1]
                if field_name != age_col:
                    continue
                if field_spec not in age_values:
                    age_values.append(field_spec)

        age_mins = [18 for i in range(0,len(age_values))]
        age_maxs = [100 for i in range(0,len(age_values))]
        for idx, agebucket in enumerate(age_values):
            if 'min' in agebucket:
                age_mins[idx] = agebucket['min']
            if 'max' in agebucket:
                age_maxs[idx] = agebucket['max']

        # find which age group (if any) is the overall age group
        idx_min = [i for i, val in enumerate(age_mins) if val == min(age_mins)]
        idx_max = [i for i, val in enumerate(age_maxs) if val == max(age_maxs)]

        idx_broadest = [idx for idx in idx_min if idx in idx_max]
        age_group_all = None
        if len(idx_broadest) != 0:
            age_group_all = age_values[idx_broadest[0]]

        result = {'age_groups': age_values,
                  'age_mins': age_mins, 'age_maxs': age_maxs,
                  'idx_mins': idx_min, 'idx_maxs': idx_max,
                  'idx_broadest_age_bracket': idx_broadest,
                  'all_ages_value': age_group_all}
        return(result)

    @staticmethod
    def get_known_sparse_queries_to_impute(query_fields, query_field_specs, curr_sparse_qset,
                                           query_indices, collection_dataframe):
        if len(curr_sparse_qset) == 0:
            return curr_sparse_qset, dict()

        geo = constants.INPUT_GEOLOCATION_FIELD
        other_fields = [q for q in query_fields if q not in {geo}]
        sparse_queries = set()
        sparse_queries_estim_ready_status = dict()

        for q in curr_sparse_qset:
            for field in other_fields:
                # if this field is already specified in the query skip it
                if len(q.intersection(query_field_specs[field])) > 0:
                    continue
                # generate new queries from combinations
                for specs in query_field_specs[field]:
                    specs = {specs}
                    newq = frozenset(q.union(specs))
                    sparse_queries.add(newq)

                    # determine the estimate ready status of this sparse query
                    idx = query_indices.get(q)
                    if idx is None: # query is not in dataframe
                        #print('Sparse query combination not in df:',q)
                        continue

                    response_field = collection_dataframe.loc[idx, constants.RESPONSE_FIELD]
                    if isinstance(response_field, bytes):
                        decoded_str = response_field.decode('utf-8')
                    else:
                        decoded_str = response_field

                    estim_ready = r'estimate_ready":true' in decoded_str

                    # print("## ---------------------------------")
                    # print("query:", q)
                    # print(idx)
                    # print(estim_ready)
                    # print(collection_dataframe.loc[idx, constants.RESPONSE_FIELD])

                    if estim_ready:
                        sparse_queries_estim_ready_status[newq] = params.DEDUCED_DATA_RESPONSE_CONTENT_ESTIM_READY
                    else:
                        sparse_queries_estim_ready_status[newq] = params.DEDUCED_DATA_RESPONSE_CONTENT_NOT_ESTIM_READY

        return sparse_queries, sparse_queries_estim_ready_status

    @staticmethod
    def impute_known_sparse_queries(query_fields, query_field_specs, curr_sparse_qset,
                                    query_indices, collection_dataframe):
        curr_sparse_qset, sparse_queries_estim_ready_status = \
            pysocialwatcher_opt.get_known_sparse_queries_to_impute(query_fields=query_fields,
                                                                   query_field_specs=query_field_specs,
                                                                   curr_sparse_qset=curr_sparse_qset,
                                                                   query_indices=query_indices,
                                                                   collection_dataframe=collection_dataframe)
        # print("Got list of sparse queries, Will begin imputing now")
        for query in curr_sparse_qset:
            idx = query_indices.get(query)
            data_response_content = sparse_queries_estim_ready_status.get(query)
            if idx is not None:
                collection_dataframe.loc[idx, constants.RESPONSE_FIELD] = data_response_content

        return curr_sparse_qset, collection_dataframe

    @staticmethod
    def get_queries_to_collect_next(k,query_fields, query_field_specs, curr_non_sparse_qset):
        geo = constants.INPUT_GEOLOCATION_FIELD
        other_fields = [q for q in query_fields if q not in {geo}]
        candid_qset = set()  # set of queries to try collecting next

        # for the first round we generate queries for (geo-location-all age/genders) combinations
        if k == 0:
            geo_iter = itertools.product(query_field_specs[geo])
            candid_qset = {frozenset(comb) for comb in geo_iter}

        else:
            for q in curr_non_sparse_qset:
                for field in other_fields:
                    # if this field is already specified in the query skip it
                    if len(q.intersection(query_field_specs[field])) > 0:
                        continue
                    # generate new queries from combinations
                    for specs in query_field_specs[field]:
                        specs = {specs}
                        newq = frozenset(q.union(specs))

                        # check if we can deduce the query's sparsity based on information we have
                        subsets = itertools.combinations(newq, len(newq)-1)
                        newq_subsets = set()
                        for sub in subsets:
                            contains_geo = len(set(sub).intersection(query_field_specs[geo])) > 0 # valid query should have geolocation
                            if contains_geo:
                                newq_subsets.add(frozenset(sub))

                        # if the query is not expected to be sparse add it to the candidate set
                        non_sparse_subsets = newq_subsets.intersection(curr_non_sparse_qset)
                        if newq_subsets.issubset(non_sparse_subsets):
                            candid_qset.add(newq)

        return candid_qset

    @staticmethod
    def get_facebook_data_for_chosen_queries(curr_candid_qset,query_indices,collection_dataframe):
        # find queries in collection dataframe and indicate for which to collect data
        num_API_calls = 0
        for query in curr_candid_qset:
            i = query_indices.get(query)
            if i is not None:
                query_response = collection_dataframe.loc[i,constants.RESPONSE_FIELD]
                if query_response == params.PLACE_HOLDER_DATA_RESPONSE_CONTENT:
                    num_API_calls += 1
                    collection_dataframe.loc[i, constants.RESPONSE_FIELD] = None  # mark row for data collection


        # perform data collection on Facebook for chosen subset of queries
        collection_dataframe = watcherAPI.perform_collection_data_on_facebook(collection_dataframe)

        # Prune the query set to exclude sparse queries
        curr_non_sparse_qset = set()
        for query in curr_candid_qset:
            i = query_indices.get(query)
            if i is not None:
                mau_estimate = collection_dataframe.loc[i, constants.MAU_UPPER_AUDIENCE_FIELD]
                if mau_estimate > params.SPARSE_QUERY_SIZE:
                    curr_non_sparse_qset.add(query)
            else:  # queries the users chose not to collect; we have no info for these so assume they are non-sparse
                curr_non_sparse_qset.add(query)

        return collection_dataframe, curr_non_sparse_qset, num_API_calls

    @staticmethod
    def print_collection_in_progress_report(collection_dataframe, k, df_num_queries, curr_candid_qset,
                                            curr_non_sparse_qset, total_API_calls_made,
                                            total_API_calls_made_with_sparse_queries,
                                            total_sparse_queries_deduced):
        incomplete = sum(
            collection_dataframe[constants.RESPONSE_FIELD] == params.PLACE_HOLDER_DATA_RESPONSE_CONTENT)
        perc_complete = float(df_num_queries - incomplete) / df_num_queries
        print("*** ----- Iteration: %d" % k)
        print("___ Num. candid queries to try generated this round: %d " % len(curr_candid_qset))
        print("___ Num. non-sparse queries this round: %d" % len(curr_non_sparse_qset))
        print("Total queries in data frame: %d" % df_num_queries)
        print("Number of queries in data frame already completed: %d" % (df_num_queries - incomplete))
        print("Total # API calls made thusfar: %d" % total_API_calls_made)
        print("Total # sparse queries thusfar: %d" % (
                    total_API_calls_made_with_sparse_queries + total_sparse_queries_deduced))
        print("__ of which, # API calls with sparse queries: %d" % total_API_calls_made_with_sparse_queries)
        print("__ of which, # queries deduced to be sparse: %d" % total_sparse_queries_deduced)
        print("Collection in progress. Perc. completed: %.2f " % (perc_complete * 100))

    @staticmethod
    def print_completed_collection_report(df_num_queries, total_API_calls_made,
                                          total_API_calls_made_with_sparse_queries, total_sparse_queries_deduced):
        print("*** ------------- Data collection completed. Summary:")
        print("Total queries in data frame: %d" % df_num_queries)
        print("Total number of API calls made: %d" % total_API_calls_made)
        print("Total number of sparse queries: %d" % (
                    total_API_calls_made_with_sparse_queries + total_sparse_queries_deduced))
        print("__ of which, API calls retuning sparse queries: %d" % total_API_calls_made_with_sparse_queries)
        print("__ of which, queries deduced to be sparse: %d" % total_sparse_queries_deduced)

    @staticmethod
    def perform_collection_data_on_facebook_with_optimization(collection_dataframe):
        df_num_queries = len(collection_dataframe.index)
        total_API_calls_made = 0
        total_API_calls_made_with_sparse_queries = 0
        total_sparse_queries_deduced = 0

        # place mock response in empty rows of response column, allowing for selective calling of
        # pySocialWatcher's data collection methods on subsets of queries
        idx = pd.isnull(collection_dataframe["response"])
        collection_dataframe.loc[idx, "response"] = params.PLACE_HOLDER_DATA_RESPONSE_CONTENT

        (query_fields, query_field_specs, query_indices) = \
            pysocialwatcher_opt.get_query_fields_and_contents(collection_dataframe)

        #if params.VERBOSE:
        #    print("The set of criteria for each targeting spec:")
        #    for field in query_field_specs:
        #        print(query_field_specs[field])

        # iteratively generate a list of queries to collect data for
        k = 0  # iteration counter (the number of fields in the query excluding geo, gender and age)
        curr_non_sparse_qset = set()
        curr_sparse_qset = set() # keeps sparse queries

        while k == 0 or len(curr_non_sparse_qset) != 0: # k <= len(query_fields)-3:
            # generate candidate queries to try next
            curr_candid_qset = pysocialwatcher_opt.get_queries_to_collect_next(k=k, query_fields=query_fields,
                                                                               query_field_specs=query_field_specs,
                                                                               curr_non_sparse_qset=curr_non_sparse_qset)

            # For the queries that can already be deduced to be sparse, impute their MAUs with 1000s
            curr_sparse_qset, collection_dataframe = \
                pysocialwatcher_opt.impute_known_sparse_queries(query_fields, query_field_specs, curr_sparse_qset,
                                                                query_indices, collection_dataframe)
            total_sparse_queries_deduced += len(curr_sparse_qset)

            # collect data from FB and determine non-sparse queries
            collection_dataframe, curr_non_sparse_qset, num_API_calls = \
                pysocialwatcher_opt.get_facebook_data_for_chosen_queries(curr_candid_qset, query_indices,
                                                                         collection_dataframe)
            curr_sparse_qset = curr_sparse_qset.union(curr_candid_qset - curr_non_sparse_qset)
            total_API_calls_made_with_sparse_queries += len(curr_candid_qset - curr_non_sparse_qset)
            total_API_calls_made += num_API_calls

            k += 1
            if params.VERBOSE:
                pysocialwatcher_opt.print_collection_in_progress_report(collection_dataframe, k, df_num_queries,
                                                                        curr_candid_qset,curr_non_sparse_qset,
                                                                        total_API_calls_made,
                                                                        total_API_calls_made_with_sparse_queries,
                                                                        total_sparse_queries_deduced)

        # impute values for the remaining known sparse queries
        while len(curr_sparse_qset) != 0:
            # For the queries that can already be deduced to be sparse, impute their MAUs with 1000s
            curr_sparse_qset, collection_dataframe = \
                pysocialwatcher_opt.impute_known_sparse_queries(query_fields, query_field_specs, curr_sparse_qset,
                                                                query_indices, collection_dataframe)
            total_sparse_queries_deduced += len(curr_sparse_qset)

            collection_dataframe, curr_non_sparse_qset, num_API_calls = \
                pysocialwatcher_opt.get_facebook_data_for_chosen_queries(set(), query_indices, collection_dataframe)

        if params.VERBOSE:
            pysocialwatcher_opt.print_completed_collection_report(df_num_queries, total_API_calls_made,
                                                                  total_API_calls_made_with_sparse_queries,
                                                                  total_sparse_queries_deduced)

        return collection_dataframe

    @staticmethod
    def rerun_data_collection(input_file_path):
        collection_dataframe = load_dataframe_from_file(input_file_path)

        not_estimate_ready = r'estimate_ready":false'

        # recode to string, conditional on data type (string vs. byte)
        collection_dataframe[constants.RESPONSE_FIELD] = collection_dataframe[constants.RESPONSE_FIELD].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
        idx_not_ready = (collection_dataframe[constants.RESPONSE_FIELD].str.contains(not_estimate_ready))
        idx_incomplete = collection_dataframe[constants.RESPONSE_FIELD] == params.PLACE_HOLDER_DATA_RESPONSE_CONTENT

        if sum(idx_incomplete) > 0:
            print("Data collection is incomplete. First complete the data collection then re-run.")
            return collection_dataframe
        if sum(idx_not_ready) > 0:
            print("Some queries are not estimate ready; Data collection will be rerun for those.")
            to_rerun = (collection_dataframe[constants.RESPONSE_FIELD].str.contains(not_estimate_ready))
            print("## Rerunning for", sum(to_rerun), "queries")
            collection_dataframe.loc[to_rerun, constants.RESPONSE_FIELD] = None

            # Run data collection
            data_collection_incomplete = True
            ntries = 0
            while data_collection_incomplete:
                try:
                    ntries = ntries + 1
                    collection_dataframe = pysocialwatcher_opt.perform_collection_data_on_facebook_with_optimization(
                        collection_dataframe)
                    data_collection_incomplete = False
                except Exception as err:
                    if ntries < params.MAX_TRY_ON_FAILED_QUERIES:
                        # still have more tries left; continue after a short wait
                        print("Found the following error: {0}".format(err))
                        print("Still have ", params.MAX_TRY_ON_FAILED_QUERIES - ntries,
                              " left. Will keep trying after ", params.SLEEP_TIME_AFTER_API_ERROR, " seconds.")
                        time.sleep(params.SLEEP_TIME_AFTER_API_ERROR)
                    else:
                        print("Found the following error: {0}".format(err))
                        print("Rerun collection is incomplete. Resume collection later!")
                        break
        else:
            print("All queries are estimate ready.")
            return collection_dataframe

        left_to_rerun = (collection_dataframe[constants.RESPONSE_FIELD].str.contains(not_estimate_ready))
        if (not data_collection_incomplete) & (sum(left_to_rerun) > 0):
            print("Rerun complete; ", sum(left_to_rerun), "queries are still not estimate ready.")
            print("Re-run the data collection later!")

        return collection_dataframe

    @staticmethod
    def process_input_json_file(json_input_file_path):

        import os
        print(os.getcwd())
        input_data_json = watcherAPI.read_json_file(json_input_file_path)

        # get the list of jsons containing different query combinations
        json_collections_list = []
        if params.JSON_WITH_PARTIAL_COMBINATIONS_FIELD in input_data_json.keys():
            base_json = {jsfield: input_data_json[jsfield] for jsfield in input_data_json.keys() if jsfield != params.JSON_WITH_PARTIAL_COMBINATIONS_FIELD}
            for target_group in input_data_json[params.JSON_WITH_PARTIAL_COMBINATIONS_FIELD]:
                json_comb = copy.deepcopy(base_json)
                for addfield in target_group.keys():
                    json_comb[addfield] = copy.deepcopy(target_group[addfield])
                json_collections_list.append(json_comb)
        else:
            json_collections_list.append(input_data_json)

        # generate the collection dataframe
        collection_dataframe = pd.DataFrame()
        for json_spec in json_collections_list:
            watcherAPI.expand_input_if_requested(json_spec)
            watcherAPI.check_input_integrity(json_spec)
            part_collection_dataframe = watcherAPI.build_collection_dataframe(json_spec)
            collection_dataframe = collection_dataframe.append(part_collection_dataframe,
                                                               ignore_index = True)

        return collection_dataframe

    """
        pySocialWatcher's data collection function modified to call the optimized data collection algorithm
    """
    @staticmethod
    def run_data_collection(json_input_file_path):
        # create collection dataframe
        collection_dataframe = pysocialwatcher_opt.process_input_json_file(json_input_file_path)

        # Run data collection
        data_collection_incomplete = True
        ntries = 0
        while data_collection_incomplete:
            try:
                ntries = ntries + 1
                collection_dataframe = pysocialwatcher_opt.perform_collection_data_on_facebook_with_optimization(collection_dataframe)
                data_collection_incomplete = False
            except Exception as err:
                if ntries < params.MAX_TRY_ON_FAILED_QUERIES:
                    # still have more tries left; continue after a short wait
                    print("Found the following error: {0}".format(err))
                    print("Still have ", params.MAX_TRY_ON_FAILED_QUERIES - ntries, " left. Will keep trying after ",
                          params.SLEEP_TIME_AFTER_API_ERROR, " seconds.")
                    time.sleep(params.SLEEP_TIME_AFTER_API_ERROR)
                else:
                    print("Found the following error: {0}".format(err))
                    print("Data collection is incomplete. Resume collection later!")
                    break

        # Report if there is need to rerun
        not_estimate_ready = r',"estimate_ready":false'
        collection_dataframe[constants.RESPONSE_FIELD] = collection_dataframe[constants.RESPONSE_FIELD].str.decode(
            'utf-8')
        idx = (collection_dataframe[constants.RESPONSE_FIELD].str.contains(not_estimate_ready))
        if (not data_collection_incomplete):
            print("Data collection completed successfully.")

            if (sum(idx) > 0):
                print("Some queries are not estimate ready:" + str(sum(idx)))
                print("Re-run data collection later!")

        return collection_dataframe

    """
        pySocialWatcher's data collection function modified to call the optimized data collection algorithm
    """
    @staticmethod
    def load_data_and_continue_collection(input_file_path):
        collection_dataframe = load_dataframe_from_file(input_file_path)

        idx = collection_dataframe[constants.RESPONSE_FIELD] == params.PLACE_HOLDER_DATA_RESPONSE_CONTENT
        if sum(idx) == 0:
            print("Data collection is already complete.")
            return collection_dataframe
        if sum(idx) > 0:
            # Run data collection
            data_collection_incomplete = True
            ntries = 0
            while data_collection_incomplete:
                try:
                    ntries = ntries + 1
                    collection_dataframe = pysocialwatcher_opt.perform_collection_data_on_facebook_with_optimization(
                        collection_dataframe)
                    data_collection_incomplete = False
                except Exception as err:
                    if ntries < params.MAX_TRY_ON_FAILED_QUERIES:
                        # still have more tries left; continue after a short wait
                        print("Found the following error: {0}".format(err))
                        print("Still have ", params.MAX_TRY_ON_FAILED_QUERIES - ntries,
                              " left. Will keep trying after ",params.SLEEP_TIME_AFTER_API_ERROR, " seconds.")
                        time.sleep(params.SLEEP_TIME_AFTER_API_ERROR)
                    else:
                        print("Found the following error: {0}".format(err))
                        print("Data collection is incomplete. Resume collection later!")
                        break

            not_estimate_ready = r',"estimate_ready":false'
            idx_rerun = (collection_dataframe[constants.RESPONSE_FIELD].str.contains(not_estimate_ready))
            if (not data_collection_incomplete):
                print("Data collection completed successfully.")
                if (sum(idx_rerun) > 0):
                    print("Some queries are not estimate ready:" + str(sum(idx_rerun)))
                    print("Re-run data collection later!")
        return collection_dataframe
