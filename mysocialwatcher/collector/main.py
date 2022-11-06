import os
from dotenv import load_dotenv
import logging
from time import sleep
from datetime import datetime, timedelta

# config
load_dotenv()  # load_dotenv('docker/collectors/saffron/ukraine_countries/.env')
data_dir = os.environ.get('DATA_DIR')  # data_dir = 'data/saffron/ukraine_countries'
specs_dir = os.environ.get('SPECS_DIR')  # specs_dir = 'docker/collectors/saffron/ukraine_countries/specs'
frequency = int(os.environ.get('FREQUENCY'))  # frequency = 1

if data_dir is None:
    data_dir = 'data'
if specs_dir is None:
    specs_dir = 'specs'
if frequency is None:
    frequency = 1

# start time
collection_start_time = datetime.now()
collection_date_stamp = collection_start_time.strftime('%Y%m%d')
collection_time_stamp = collection_start_time.strftime('%H%M%S')

# logging
os.makedirs(os.path.join(data_dir, 'logs'), exist_ok=True)
logging.basicConfig(
    filename=os.path.join(data_dir, 'logs', collection_date_stamp + '_' + collection_time_stamp + '.log'),
    format='%(asctime)s (%(levelname)s) - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from pysocialwatcher import watcherAPI, constants


if __name__ == '__main__':

    # specs
    files = os.listdir(specs_dir)
    files = [f for f in files if f.endswith('.json')]
    files.sort()

    for file in files:

        try:

            # specs start time
            spec_start_time = datetime.now()
            spec_time_stamp = spec_start_time.strftime('%H%M%S')
            spec_date_stamp = spec_start_time.strftime('%Y%m%d')

            specs_filepath = os.path.abspath(os.path.join('specs', file))
            if specs_filepath is None:
                raise Exception('Error: Specs filepath is non-existent.')
            elif not specs_filepath.endswith('.json'):
                logger.warning(f'Skipping specs ({specs_filepath}) that do not have a .json file extension.')
                next

            specs_name = os.path.splitext(os.path.basename(specs_filepath))[0]

            logger.info(' ')
            logger.info('--------------------------------------------------')
            logger.info('Preparing collection with specification: ' + specs_name)

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

        except:
            logger.error('An error occurred while preparing to collect data.', exc_info=True)

        # determine if previous collection should be continued
        try:
            continue_previous_collection = False

            temporary_file = os.path.join(data_dir,
                                          "collecting/dataframe_collecting_" + specs_name + "_" + spec_date_stamp + ".csv")

            existing_temp_files = os.listdir(os.path.join(data_dir, 'collecting'))
            existing_temp_files = [f for f in existing_temp_files if specs_name in f]
            existing_temp_files.sort()

            if os.path.exists(temporary_file):
                continue_previous_collection = True

            elif frequency > 1 and len(existing_temp_files) > 0:

                latest_temp_file = existing_temp_files[-1]

                latest_finished_file = latest_temp_file.replace('dataframe_collecting_',
                                                                'dataframe_collected_finished_')
                latest_finished_file = os.path.join(data_dir, latest_finished_file)

                latest_date = os.path.splitext(latest_temp_file)[0].split('_')[-1]
                latest_date = datetime.date(datetime.strptime(latest_date, '%Y%m%d'))
                cutoff_date = datetime.date(datetime.now()) - timedelta(days=frequency)

                if not os.path.exists(latest_finished_file) and latest_date >= cutoff_date:
                    continue_previous_collection = True
                    spec_date_stamp = latest_date.strftime('%Y%m%d')
                    # temporary_file = os.path.join(data_dir, 'collecting', latest_temp_file)

        except:
            continue_previous_collection = False
            logger.warning('An error occurred while checking for previous collections to continue. '
                           'Beginning new collection.', exc_info=True)

        # reconfigure temporary file locations
        constants.DATAFRAME_SKELETON_FILE_NAME = \
            "skeleton/dataframe_skeleton_" + specs_name + "_" + spec_date_stamp + ".csv"
        constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME = \
            "collecting/dataframe_collecting_" + specs_name + "_" + spec_date_stamp + ".csv"
        constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME = \
            "finished/dataframe_collected_finished_" + specs_name + "_" + spec_date_stamp + ".csv"

        # continue a previous collection
        if continue_previous_collection:
            try:
                logger.info('Continuing a previous collection: ' + temporary_file)

                df = watcher.load_data_and_continue_collection(
                    input_file_path=os.path.join(data_dir, constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME),
                    output_dir=data_dir + '/',
                    remove_tmp_files=False)

            except:
                logger.warning('An error occurred while continuing a previous collection.', exc_info=True)
                continue_collection = False

        # start a new collection
        if not continue_previous_collection:
            try:
                logger.info('Beginning a new collection: ' + temporary_file)

                df = watcher.run_data_collection(
                    json_input_file_path=specs_filepath,
                    output_dir=data_dir + '/',
                    remove_tmp_files=False)

            except:
                logger.error('An error occurred while collecting new data.', exc_info=True)

        del watcher

    # Sleep until midnight if collection completed in less than 24 hours
    duration = datetime.now() - collection_start_time
    if duration < timedelta(hours=24):
        now = datetime.now()
        tomorrow = datetime(now.year, now.month, now.day) + timedelta(1)

        sleep_duration = tomorrow - now
        if sleep_duration.seconds > 0:
            logging.info('Sleeping until tomorrow (' + str(sleep_duration) + ').')
            sleep(sleep_duration.seconds)
