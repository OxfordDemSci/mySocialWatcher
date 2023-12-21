from mysocialwatcher.collector.utils import *
from pysocialwatcher import watcherAPI, constants
from mysocialwatcher.collector.pysocialwatcher_opt import pysocialwatcher_opt



if __name__ == '__main__':

    logger.info(' ')
    logger.info('--------------------------------------------------')
    logger.info(logger.handlers[0].baseFilename)

    logger.info('Sleep time: ' + sleep_time)
    logger.info('pysocialwatcher_opt: ' + pysocialwatcher_opt_flag)

    # set pysocialwatcher_opt_flag to boolean 
    pysocialwatcher_opt_flag = (pysocialwatcher_opt_flag.lower() == 'true')

    specs_list = get_specs_list(specs_dir=specs_dir,
                                data_dir=data_dir)

    for specs_filename in specs_list:
        # specs_filename = specs_list[0]

        # ---- prepare to collect data ---- #
        try:

            # data directories
            os.makedirs(data_dir, exist_ok=True)
            os.makedirs(os.path.join(data_dir, 'skeleton'), exist_ok=True)
            os.makedirs(os.path.join(data_dir, 'collecting'), exist_ok=True)
            os.makedirs(os.path.join(data_dir, 'finished'), exist_ok=True)

            specs_filepath = os.path.abspath(os.path.join('specs', specs_filename))
            if specs_filepath is None:
                raise Exception('Error: Specs filepath does not exist.')

            # temporary file locations
            df_names = get_df_names(data_dir=data_dir, specs_filename=specs_filename)

            # check if collection already completed for the day
            if os.path.exists(os.path.join(data_dir, df_names.get('finished'))):
                continue

            # start log
            logger.info('Preparing collection with specification: ' + specs_filepath)

            # instantiate watcher, depending on whether argument pysocialwatcher_opt is true
            if pysocialwatcher_opt_flag:
                watcher = pysocialwatcher_opt(api_version='17.0',
                                              sleep_time=int(sleep_time),
                                              save_every_x=100)
            else:
                watcher = watcherAPI(api_version='17.0',
                                     sleep_time=int(sleep_time),
                                     save_every_x=100,
                                     verbose=False)

            # load credentials
            watcher.load_credentials_file('credentials.csv')

            # configure temporary files
            constants.DATAFRAME_SKELETON_FILE_NAME = df_names.get('skeleton')
            constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME = df_names.get('collecting')
            constants.DATAFRAME_AFTER_COLLECTION_FILE_NAME = df_names.get('finished')

        except:
            logger.error('An error occurred while preparing to collect data.', exc_info=True)

        # ---- continue a previous collection ---- #
        continue_previous_collection = df_names.get('continue_previous_collection')
        if continue_previous_collection:
            try:
                logger.info('Continuing a previous collection: ' + df_names.get('collecting'))

                df = watcher.load_data_and_continue_collection(
                    input_file_path=os.path.join(data_dir, constants.DATAFRAME_TEMPORARY_COLLECTION_FILE_NAME),
                    output_dir=data_dir + '/',
                    remove_tmp_files=True)
            except:
                logger.warning('An error occurred while continuing a previous collection.', exc_info=True)
                continue_previous_collection = False

        # ---- start a new collection ---- #
        if not continue_previous_collection:
            try:
                logger.info('Beginning a new collection: ' + df_names.get('collecting'))

                df = watcher.run_data_collection(
                    json_input_file_path=specs_filepath,
                    output_dir=data_dir + '/',
                    remove_tmp_files=True)
            except:
                logger.error('An error occurred while collecting new data.', exc_info=True)

        logger.info('Finished collection: ' + df_names.get('collecting'))
        del watcher

    logger.info('Finished collection.')
