import os
import logging
import datetime
from time import sleep

data_dir = 'data'  # data_dir = 'data/saffron/ukraine_regions'
specs_dir = 'specs'  # specs_dir = 'docker/collectors/saffron/ukraine_regions/specs'

# start time
collection_start_time = datetime.datetime.now()

# logging
log_dir = os.path.join(data_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, collection_start_time.strftime('%Y%m%d_%H%M%S') + '.log'),
    format='%(asctime)s (%(levelname)s) - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_specs_list():

    specs_list = os.listdir(specs_dir)
    specs_list = [f for f in specs_list if f.endswith('.json')]
    specs_list.sort()

    finished_list = os.listdir(os.path.join(data_dir, 'finished'))

    most_recent_specs = {}
    for specs in specs_list:
        # specs = specs_list[0]

        specs_name = os.path.splitext(specs)[0]

        specs_finished = [i for i in finished_list if specs_name in i]
        specs_finished.sort(reverse=True)
        if len(specs_finished) > 0:
            most_recent_specs[specs] = int(specs_finished[0].split(sep='_')[-1].split(sep='.')[0])

    drop_specs = []
    current_date = int(datetime.datetime.now().strftime('%Y%m%d'))
    for i in range(len(most_recent_specs)-1):

        i_date = list(most_recent_specs.values())[i]
        if i_date == current_date or i_date > list(most_recent_specs.values())[i+1]:
            drop_specs.append(list(most_recent_specs.keys())[i])

    if list(most_recent_specs.values())[-1] == current_date:
        drop_specs.append(list(most_recent_specs.keys())[-1])

    result = [i for i in specs_list if i not in drop_specs]
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
            logger.info('Sleeping until tomorrow (' + str(sleep_duration) + ').')
            sleep(sleep_duration.seconds)
