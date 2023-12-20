"""

Description: Parameter values for the pySocialWatcher optimization module.

"""

SPARSE_QUERY_SIZE = 1000 # size of FB's sparse queries
VERBOSE = True  # should additional info about data collection be provided

MAX_TRY_ON_FAILED_QUERIES = 5 # max number of tries when the API give errors
SLEEP_TIME_AFTER_API_ERROR = 500 # time in seconds to wait after the API gives an error before retrying

ALL_GENDERS_VALUE = 0 # API parameter value for all genders 

JSON_WITH_PARTIAL_COMBINATIONS_FIELD = 'target_groups'

PLACE_HOLDER_NUMERIC = -1
PLACE_HOLDER_DATA_RESPONSE_CONTENT = r'{"data":[{"daily_outcomes_curve":' \
                                     r'[{"spend":0,"reach":0,"impressions":0,"actions":0}],' \
                                     r'"estimate_dau":' + str(PLACE_HOLDER_NUMERIC) + \
                                     r',"estimate_mau":' + str(PLACE_HOLDER_NUMERIC) + \
                                     r',"estimate_mau_lower_bound":' + str(PLACE_HOLDER_NUMERIC) + \
                                     r',"estimate_mau_upper_bound":' + str(PLACE_HOLDER_NUMERIC) + \
                                     r',"estimate_ready":false}]}'

DEDUCED_DATA_RESPONSE_CONTENT_ESTIM_READY = r'{"data":[{"daily_outcomes_curve":' \
                                            r'[{"spend":0,"reach":0,"impressions":0,"actions":0}],' \
                                            r'"estimate_dau":' + str(PLACE_HOLDER_NUMERIC) + \
                                            r',"estimate_mau":' + str(SPARSE_QUERY_SIZE) + \
                                            r',"estimate_mau_lower_bound":' + str(PLACE_HOLDER_NUMERIC) + \
                                            r',"estimate_mau_upper_bound":' + str(SPARSE_QUERY_SIZE) + \
                                            r',"estimate_ready":true}]}'
DEDUCED_DATA_RESPONSE_CONTENT_NOT_ESTIM_READY = r'{"data":[{"daily_outcomes_curve":' \
                                                r'[{"spend":0,"reach":0,"impressions":0,"actions":0}],' \
                                                r'"estimate_dau":' + str(PLACE_HOLDER_NUMERIC) + \
                                                r',"estimate_mau":' + str(SPARSE_QUERY_SIZE) + \
                                                r',"estimate_mau_lower_bound":' + str(PLACE_HOLDER_NUMERIC) + \
                                                r',"estimate_mau_upper_bound":' + str(SPARSE_QUERY_SIZE) + \
                                                r',"estimate_ready":false}]}'
