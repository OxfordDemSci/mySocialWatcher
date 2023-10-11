import os
from pysocialwatcher.utils import load_dataframe_from_file

data_dir = 'data'

file_list = []
for (root, dirs, file) in os.walk(data_dir):
    for f in file:
        full_path = os.path.join(root, f)
        if "finished/dataframe_collected_finished_" in full_path:
            file_list.append(full_path)

for file in file_list:
    # file = file_list[0]
    print(file)

    skeleton = file.replace('finished/dataframe_collected_finished_', 'skeleton/dataframe_skeleton_')
    collecting = file.replace('finished/dataframe_collected_finished_', 'collecting/dataframe_collecting_')
    if os.path.exists(skeleton):
        os.remove(skeleton)
    if os.path.exists(collecting):
        os.remove(collecting)
