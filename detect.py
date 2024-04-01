import os
import glob
import json

folder_path = 'uploads/'  # Replace with the actual folder path
info_files = glob.glob(os.path.join(folder_path, '*.info'))

    
table_data = []
for info_file in info_files:
    with open(info_file, 'r') as file:
        file_metadata = json.load(file)

        
        # row = {
        #     'ID': file_metadata.get('ID', 'NA'),
        #     'Size': file_metadata.get('Size', 'NA'),
        #     'SizeIsDeferred': file_metadata.get('SizeIsDeferred', 'NA'),
        #     'Offset': file_metadata.get('Offset', 'NA'),
        #     'eegDataType': file_metadata['MetaData'].get('eegDataType', 'NA'),
        #     'email': file_metadata['MetaData'].get('email', 'NA'),
        #     'filename': file_metadata['MetaData'].get('filename', 'NA'),
        #     'filetype': file_metadata['MetaData'].get('filetype', 'NA'),
        #     'jobType': file_metadata['MetaData'].get('jobType', 'NA'),
        #     'name': file_metadata['MetaData'].get('name', 'NA'),
        #     'projectDescription': file_metadata['MetaData'].get('projectDescription', 'NA'),
        #     'projectName': file_metadata['MetaData'].get('projectName', 'NA'),
        #     'relativePath': file_metadata['MetaData'].get('relativePath', 'NA'),
        #     'type': file_metadata['MetaData'].get('type', 'NA'),
        #     'IsPartial': file_metadata.get('IsPartial', 'NA'),
        #     'IsFinal': file_metadata.get('IsFinal', 'NA'),
        #     'PartialUploads': file_metadata.get('PartialUploads', 'NA'),
        #     'StoragePath': file_metadata['Storage'].get('Path', 'NA'),
        #     'StorageType': file_metadata['Storage'].get('Type', 'NA'),
        #     'status': 'pending'
        # }
        row = {
            'status': 'pending',
            'filename': file_metadata['MetaData'].get('filename', 'NA'),
            'eegDataType': file_metadata['MetaData'].get('eegDataType', 'NA'),
            'jobType': file_metadata['MetaData'].get('jobType', 'NA'),
            'StoragePath': file_metadata['Storage'].get('Path', 'NA'),
            'ID': file_metadata.get('ID', 'NA'),
            'email': file_metadata['MetaData'].get('email', 'NA')
        }
        table_data.append(row)

    import pandas as pd

    # Convert the table_data list to a pandas DataFrame
    df = pd.DataFrame(table_data)


