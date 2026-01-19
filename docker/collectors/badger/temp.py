import os
from pathlib import Path

folder_name = "docker/collectors/badger/dgg_subnational_tessellated_device_ins/specs"

files = os.listdir(folder_name)

for file in files:
    if file.endswith('json'):
        file_path = Path(folder_name) / file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Replace "facebook" with "instagram"
        updated_content = content.replace('"facebook"', '"instagram"')
        
        with open(file_path, 'w') as f:
            f.write(updated_content)