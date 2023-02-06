from pysocialwatcher import watcherAPI

if __name__ == '__main__':

    # instantiate watcher
    watcher = watcherAPI(api_version='16.0',
                         sleep_time=11,
                         save_every_x=100,
                         verbose=False)

    # load credentials
    watcher.load_credentials_file('docker/collectors/stitch/turkey_earthquake/credentials.csv')

    # test credentials
    watcher.check_tokens_account_valid()

