import gzip


def gunzip(source_filepath, dest_filepath, block_size=65536):
    """unzip .csv.gz files from pySocialWatcher"""
    with gzip.open(source_filepath, 'rb') as s_file, open(dest_filepath, 'wb') as d_file:
        while True:
            block = s_file.read(block_size)
            if not block:
                break
            else:
                d_file.write(block)
