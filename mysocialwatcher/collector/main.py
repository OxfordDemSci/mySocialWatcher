import sys
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from mysocialwatcher.collector.utils import submit_psw_csv
from pysocialwatcher import watcherAPI, constants

# environment variables
load_dotenv()

# log file
os.makedirs(os.path.join('data', 'logs'), exist_ok=True)
timestamp = str(int(datetime.timestamp(datetime.now())))
logfile = os.path.join('data', 'logs', timestamp + '.log')
logging.basicConfig(filename=logfile,
                    level=logging.INFO,
                    format='%(asctime)s (%(levelname)s) - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')


if __name__ == '__main__':

    try:

        # command line argument
        if sys.argv[1] is not None:
            specs_filepath = os.path.abspath(sys.argv[1])
        else:
            files = os.listdir('./specs')
            files = [f for f in files if f.endswith('.json')]
            specs_filepath = os.path.join('specs', files[0])

        if specs_filepath is None or not specs_filepath.endswith('.json'):
            raise Exception('Error: No collection specs could be found.')

        # data directories
        data_directory = 'data'
        os.makedirs(data_directory, exist_ok=True)
        os.makedirs(os.path.join(data_directory, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(data_directory, 'skeleton'), exist_ok=True)
        os.makedirs(os.path.join(data_directory, 'collecting'), exist_ok=True)
        os.makedirs(os.path.join(data_directory, 'finished'), exist_ok=True)

        # instantiate watcher
        watcher = watcherAPI(api_version='15.0', sleep_time=20)

        # load credentials
        watcher.load_credentials_file('credentials.csv')

        # reconfigure temporary file locations
        constants.DATAFRAME_SKELETON_FILE_NAME = (
                "/skeleton/dataframe_skeleton_" + timestamp + ".csv")
        constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME = (
                "/collecting/dataframe_collecting_" + timestamp + ".csv")
        constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME = (
                    "/finished/dataframe_collected_finished_" + timestamp + ".csv")
        constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME_WITHOUT_FULL_RESPONSE = (
                    "/clean/collect_finished_clean" + timestamp + ".csv")

        # collect data
        df = watcher.run_data_collection(json_input_file_path=specs_filepath,
                                         output_dir=data_directory,
                                         remove_tmp_files=False)

        # write collection to SQL via API
        response = submit_psw_csv(
            filename=os.path.join('data', 'finished', 'dataframe_collected_finished_' + timestamp + '.csv'),
            token=os.environ['DATABASE_TOKEN'],
            platform='facebook',
            country='XX',
            valid=True)

        # save API responses
        # response.to_csv(os.path.join('data', 'logs', str(timestamp) + '_sql.csv'))

    except Exception as e:

        # log exception
        logging.error('Exception:', exc_info=e)

        # healthcheck.io fail notification
        # requests.get('https://hc-ping.com/' + os.environ['HEALTHCHECK_UUID'] + '/fail')

    finally:

        # move logfile to data directory
        os.makedirs(os.path.join('data', 'logs'), exist_ok=True)
        os.rename(logfile, os.path.join('data', 'logs', os.path.basename(logfile)))

