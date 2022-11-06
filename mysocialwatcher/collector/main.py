import sys
import os
import logging
from time import sleep
from datetime import datetime, timedelta
from dotenv import load_dotenv

# environment variables
load_dotenv()

if __name__ == '__main__':

    collection_start_time = datetime.now()

    # specs
    specs_dir = 'specs'
    files = os.listdir(specs_dir)
    files = [f for f in files if f.endswith('.json')]
    files.sort()

    for file in files:

        try:

            specs_filepath = os.path.abspath(os.path.join('specs', file))

            if specs_filepath is None or not specs_filepath.endswith('.json'):
                raise Exception('Error: No collection specs could be found.')

            specs_name = os.path.splitext(os.path.basename(specs_filepath))[0]

            # start time
            spec_start_time = datetime.now()
            time_stamp = spec_start_time.strftime('%H%M%S')
            date_stamp = spec_start_time.strftime('%Y%m%d')

            # logging
            data_dir = 'data'
            os.makedirs(os.path.join(data_dir, 'logs'), exist_ok=True)
            logging.basicConfig(
                filename=os.path.join(data_dir, 'logs', specs_name + '_' + date_stamp + '_' + time_stamp + '.log'),
                format='%(asctime)s (%(levelname)s) - %(message)s',
                datefmt='%d-%b-%y %H:%M:%S',
                filemode='a')
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)

            logger.info(' ')
            logger.info('--------------------------')
            logger.info('Preparing to collect data.')

            from pysocialwatcher import watcherAPI, constants

            # data directories
            os.makedirs(data_dir, exist_ok=True)
            os.makedirs(os.path.join(data_dir, 'logs'), exist_ok=True)
            os.makedirs(os.path.join(data_dir, 'skeleton'), exist_ok=True)
            os.makedirs(os.path.join(data_dir, 'collecting'), exist_ok=True)
            os.makedirs(os.path.join(data_dir, 'finished'), exist_ok=True)

            # instantiate watcher
            watcher = watcherAPI(api_version='15.0',
                                 sleep_time=12,
                                 save_every_x=100)

            # load credentials
            watcher.load_credentials_file('credentials.csv')

            # reconfigure temporary file locations
            constants.DATAFRAME_SKELETON_FILE_NAME = \
                "skeleton/dataframe_skeleton_" + specs_name + "_" + date_stamp + ".csv"
            constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME = \
                "collecting/dataframe_collecting_" + specs_name + "_" + date_stamp + ".csv"
            constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME = \
                "finished/dataframe_collected_finished_" + specs_name + "_" + date_stamp + ".csv"
            constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME_WITHOUT_FULL_RESPONSE = \
                "clean/collect_finished_clean_" + specs_name + "_" + date_stamp + ".csv"

            temporary_file = os.path.join(data_dir, constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME)
            continue_collection = os.path.exists(temporary_file)

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
                    output_dir=data_dir + '/',
                    remove_tmp_files=False)

            except:
                logger.error('An error occurred while collecting new data.', exc_info=True)

    duration = datetime.now() - collection_start_time
    if duration < timedelta(hours=24):
        now = datetime.now()
        tomorrow = datetime(now.year, now.month, now.day) + timedelta(1)

        sleep_duration = tomorrow - now
        if sleep_duration.seconds > 0:
            logging.info('Sleeping until tomorrow (' + str(sleep_duration) + ').')
            sleep(sleep_duration.seconds)
