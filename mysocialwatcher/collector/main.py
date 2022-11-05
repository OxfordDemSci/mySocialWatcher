import sys
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# environment variables
load_dotenv()

# start time
timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
day_stamp = datetime.now().strftime('%Y-%m-%d')

# logging
os.makedirs(os.path.join('data', 'logs'), exist_ok=True)
logging.basicConfig(filename=os.path.join('data', 'logs', timestamp + '.log'),
                    format='%(asctime)s (%(levelname)s) - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from pysocialwatcher import watcherAPI, constants


if __name__ == '__main__':

    try:

        logger.info('Preparing to collect data.')

        # command line argument
        if sys.argv[1] is None:
            files = os.listdir('./specs')
            files = [f for f in files if f.endswith('.json')]
            specs_filepath = os.path.join('specs', files[0])
        else:
            specs_filepath = os.path.abspath(sys.argv[1])

        if specs_filepath is None or not specs_filepath.endswith('.json'):
            raise Exception('Error: No collection specs could be found.')

        # data directories
        data_dir = 'data'
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'skeleton'), exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'collecting'), exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'finished'), exist_ok=True)

        # reconfigure temporary file locations
        constants.DATAFRAME_SKELETON_FILE_NAME = "/skeleton/dataframe_skeleton_" + day_stamp + ".csv"
        constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME = "/collecting/dataframe_collecting_" + day_stamp + ".csv"
        constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME = "/finished/dataframe_collected_finished_" + day_stamp + ".csv"
        constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME_WITHOUT_FULL_RESPONSE = \
            "/clean/collect_finished_clean" + day_stamp + ".csv"

        temporary_file = data_dir + constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME
        continue_collection = os.path.exists(temporary_file)

        # instantiate watcher
        watcher = watcherAPI(api_version='15.0',
                             sleep_time=12,
                             save_every_x=100)

        # load credentials
        watcher.load_credentials_file('credentials.csv')

    except:
        logger.error('An error occurred while preparing to collect data.', exc_info=True)


    # continue a previous collection
    if continue_collection:
        try:
            logger.info('Continuing a previous collection: ' + temporary_file)

            df = watcher.load_data_and_continue_collection(
                input_file_path=temporary_file)

        except:
            logger.warning('An error occurred while continuing a previous collection.', exc_info=True)
            continue_collection = False

    # start a new collection
    if not continue_collection:
        try:
            logger.info('Beginning a new collection: ' + temporary_file)

            df = watcher.run_data_collection(
                json_input_file_path=specs_filepath,
                output_dir=data_dir,
                remove_tmp_files=False)

        except:
            logger.error('An error occurred while collecting new data.', exc_info=True)
