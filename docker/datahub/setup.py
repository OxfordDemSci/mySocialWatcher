import os
import shutil


if __name__ == '__main__':

    # environment
    shutil.copy(src=os.path.join('config', 'private', 'datahub.env'),
                dst=os.path.join('docker', 'datahub', '.env'))

