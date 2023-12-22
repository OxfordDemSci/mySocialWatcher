import os
import logging
import datetime
import json
from time import sleep
from dotenv import load_dotenv
load_dotenv()

# directories
data_dir = 'data'  # data_dir = 'data/saffron/ukraine_regions'
specs_dir = 'specs'  # specs_dir = 'docker/collectors/saffron/ukraine_regions/specs'

# sleep time
sleep_time = 11
if os.getenv('sleep_time') is not None:
    sleep_time = os.getenv('sleep_time')

# pysocialwatcher_opt
pysocialwatcher_opt_flag = False
if os.getenv('pysocialwatcher_opt_flag') is not None:
    pysocialwatcher_opt_flag = os.getenv('pysocialwatcher_opt_flag')

# betterestimates_flag
betterestimates_flag = False
if os.getenv('betterestimates_flag') is not None:
    betterestimates_flag = os.getenv('betterestimates_flag')

# logging
os.makedirs(os.path.join(data_dir, 'logs'), exist_ok=True)
logging.basicConfig(
    filename=os.path.join(os.path.join(data_dir, 'logs'),
                          datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.log'),
    format='%(asctime)s (%(levelname)s) - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# need to config logging before importing from pysocialwatcher, else its logger config will take priority
from pysocialwatcher.utils import get_all_combinations_from_input


def get_specs_list(specs_dir, data_dir):

    specs_list = os.listdir(specs_dir)
    specs_list = [f for f in specs_list if f.endswith('.json')]
    specs_list.sort()

    finished_list = []
    if os.path.exists(os.path.join(data_dir, 'finished')):
        finished_list = os.listdir(os.path.join(data_dir, 'finished'))

    collecting_list = []
    if os.path.exists(os.path.join(data_dir, 'collecting')):
        collecting_list = os.listdir(os.path.join(data_dir, 'collecting'))

    finished_latest = {}
    for specs in specs_list:
        # specs = specs_list[0]

        specs_name = os.path.splitext(specs)[0]

        specs_finished = [i for i in finished_list if specs_name in i]
        specs_finished.sort(reverse=True)

        specs_collecting = [i for i in collecting_list if specs_name in i]

        if len(specs_collecting) > 0:
            finished_latest[specs] = -1
        elif len(specs_finished) == 0:
            finished_latest[specs] = 0
        elif len(specs_finished) > 0:
            finished_latest[specs] = int(specs_finished[0].split(sep='_')[-1].split(sep='.')[0])

    # sort by latest finished date
    finished_latest = dict(sorted(finished_latest.items(), key=lambda kv: (kv[1], kv[0])))

    result = list(finished_latest.keys())
    return result


def get_df_names(data_dir, specs_filename):
    # data_dir = 'data/_test/_test'
    # specs_filename = 'specs001.json'

    specs_name = specs_filename.rstrip('.json')

    collecting_list = os.listdir(os.path.join(data_dir, 'collecting'))
    collecting_list = [i for i in collecting_list if specs_name in i]
    collecting_list.sort()

    if len(collecting_list) > 0:
        date_stamp = collecting_list[-1].rstrip('.csv.gz').split('_')[-1]
        continue_previous_collection = True
    else:
        date_stamp = datetime.datetime.now().strftime('%Y%m%d')
        continue_previous_collection = False

    result = {'skeleton': os.path.join('skeleton',
                                       'dataframe_skeleton_' + specs_name + '_' + date_stamp + '.csv.gz'),
              'collecting': os.path.join('collecting',
                                         'dataframe_collecting_' + specs_name + '_' + date_stamp + '.csv.gz'),
              'finished': os.path.join('finished',
                                       'dataframe_collected_finished_' + specs_name + '_' + date_stamp + '.csv.gz'),
              'continue_previous_collection': continue_previous_collection}
    return result


def sleep_the_day(start_time):
    duration = datetime.datetime.now() - start_time
    if duration < datetime.timedelta(hours=24):
        now = datetime.datetime.now()
        tomorrow = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)

        sleep_duration = tomorrow - now
        if sleep_duration.seconds > 0:
            sleep(sleep_duration.seconds)


def estimate_run_time(specs_dir, n_tokens=1, sleep_time=11):
    runtime = 0
    specs_list = os.listdir(specs_dir)
    for specs_file in specs_list:
        with open(os.path.join(specs_dir, specs_file)) as f:
            specs = json.load(f)
        runtime += len(get_all_combinations_from_input(specs)) * sleep_time / n_tokens
    return str(datetime.timedelta(seconds=runtime))
