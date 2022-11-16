import os
import shutil


if __name__ == '__main__':

    # environment
    shutil.copy(src=os.path.join('config', 'private', 'crawler.env'),
                dst=os.path.join('docker', 'crawler', '.env'))

