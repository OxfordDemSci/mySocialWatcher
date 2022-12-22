from pysocialwatcher import watcherAPI, constants
from pysocialwatcher.utils import *
import time
import pickle
import os


def psw_request(watcher, json_input_file_path, data_dir):

    # format arguments
    output_dir = data_dir + '/'

    # ---- watcherAPI.run_data_collection() ----#
    input_data_json = watcher.read_json_file(json_input_file_path)
    watcher.expand_input_if_requested(input_data_json)
    watcher.check_input_integrity(input_data_json)
    collection_dataframe = watcher.build_collection_dataframe(input_data_json, output_dir)

    # ---- watcher.perform_collection_data_on_facebook ----#
    dataframe_with_uncompleted_requests = collection_dataframe[pd.isnull(collection_dataframe["response"])]
    rows_to_request = dataframe_with_uncompleted_requests.head(len(constants.TOKENS))

    # ---- trigger_request_process_and_return_response ----#
    for index, row in rows_to_request.iterrows():
        break
    token, account = get_token_and_account_number_or_wait()

    # ---- trigger_facebook_call ----#

    # ---- call_request_fb ----#
    target_request = row[constants.TARGETING_FIELD]
    payload = {
        'optimization_goal': "AD_RECALL_LIFT",
        'targeting_spec': json.dumps(target_request),
        'access_token': token,
    }

    # ---- send_request ----#
    response = requests.get(url=constants.REACHESTIMATE_URL.format(account),
                            params=payload,
                            timeout=constants.REQUESTS_TIMEOUT)

    # remove temporary files
    for file in [constants.DATAFRAME_SKELETON_FILE_NAME, constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME]:
        if os.path.exists(output_dir + file):
            os.remove(output_dir + file)

    return response


if __name__ == '__main__':

    # access token
    credentials_path = './docker/collectors/bester/dailyuk/credentials.csv'

    # data path
    data_dir = './data/tmp'
    os.makedirs(data_dir, exist_ok=True)

    # specs
    json_input_file_path = 'config/specs/templates/US_regions.json'

    # instantiate pySocialWatcher
    watcher = watcherAPI(api_version='15.0',
                         sleep_time=0,
                         verbose=False)

    # load credentials
    watcher.load_credentials_file(credentials_path)
    watcher.check_tokens_account_valid()

    # single collect
    response = psw_request(watcher=watcher,
                           json_input_file_path=json_input_file_path,
                           data_dir=data_dir)

    print(str(response.status_code))
    print(str(response.json()))

    # generate a token error
    t0 = time.time()
    for i in range(302):
        response = psw_request(watcher=watcher,
                               json_input_file_path=json_input_file_path,
                               data_dir=data_dir)

        elapsed_time = time.time() - t0
        print('Request: ' + str(i + 1))
        print('Elapsed time: ' + str(elapsed_time) + ' seconds')
        print('Requests per hour: ' + str(i / (elapsed_time/3600)))
        print('Status: ' + str(response.status_code))
        print('Response: ' + str(response.json()))
        print(' ')

        if response.status_code != 200:
            with open(os.path.join(data_dir, 'response.pkl'), 'wb') as file:
                pickle.dump(response, file)
            break


    # load and evaluate token error response
    with open(os.path.join(data_dir, 'response.pkl'), 'rb') as file:
        response = pickle.load(file)

    # error_json as in pysocialwatcher.utils.handle_send_request_error
    error_json = json.loads(response.text)

    # calculate appropriate rest times
    def rest_time(SLEEP_TIME=12, LIMIT_CALLS_PER_HOUR=300):

        rest_time = min(30 * 60, max(1 * 60, 3600 - (SLEEP_TIME * LIMIT_CALLS_PER_HOUR)))

        print(f"Too many calls to this ad-account (SLEEP_TIME={SLEEP_TIME}). We will rest for {round(rest_time/60)} minutes "
              f"and then try again.")

        return rest_time

    for i in range(1, 20):
        rest_time(i)







