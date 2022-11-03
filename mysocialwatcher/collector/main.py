import sys
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from mysocialwatcher.collector.utils import submit_psw_csv

# environment variables
load_dotenv()

# start time
timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

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

    except Exception as e:

        # log exception
        logger.error('Exception:', exc_info=e)
