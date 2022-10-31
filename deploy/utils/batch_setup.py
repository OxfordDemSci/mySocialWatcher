import os

if __name__ == "__main__":

    dir_path = os.path.join('deploy', 'docker')

    for root, dirs, files in os.walk(dir_path, ):
        for file in files:
            if file == 'setup.py':
                print(os.path.join(root, file))
                os.system('python3 ' + os.path.join(root, file))
