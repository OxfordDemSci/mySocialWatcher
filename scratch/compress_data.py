import os
from pysocialwatcher.utils import load_dataframe_from_file

file_list = []
for (root, dirs, file) in os.walk(data_dir):
    for f in file:
        full_path = os.path.join(root, f)
        if "finished/dataframe_collected_finished_" in full_path and os.path.splitext(f)[1] == '.csv':
            file_list.append(full_path)
    for f in file:
        full_path = os.path.join(root, f)
        if "collecting/dataframe_collecting_" in full_path and os.path.splitext(f)[1] == '.csv':
            file_list.append(full_path)
    for f in file:
        full_path = os.path.join(root, f)
        if "skeleton/dataframe_skeleton_" in full_path and os.path.splitext(f)[1] == '.csv':
            file_list.append(full_path)
file_list.reverse()

for file in file_list:
    # file = file_list[10]
    print(file)
    x = load_dataframe_from_file(file)
    x.to_csv(file + '.gz')
    os.remove(file)
