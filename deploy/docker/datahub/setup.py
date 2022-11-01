import os
import shutil


if __name__ == '__main__':

    # environment
    shutil.copy(src=os.path.join('deploy', 'private', 'datahub.env'),
                dst=os.path.join('deploy', 'docker', 'datahub', '.env'))

