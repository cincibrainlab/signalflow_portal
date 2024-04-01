import os
import glob
import csv
import json
import shutil

def process_eeg_files():
    upload_folder = 'uploads/'
    input_folder = 'input/'
    info_archive_folder = 'info_archive/'
    results_folder = 'results/'

    # Create directories if they don't exist
    for folder in [upload_folder, input_folder, info_archive_folder, results_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    
    
    info_files = glob.glob(os.path.join(upload_folder, '*.info'))
    
    for info_file in info_files:
        with open(info_file, 'r') as file:
            file_metadata = json.load(file)
            
            metadata = file_metadata.get('MetaData', {})
            filename = metadata.get('filename', 'N/A')
            filetype = metadata.get('filetype', 'N/A')
            name = metadata.get('name', 'N/A')
            
            # Step 1: Recreate the file from the info file and move to input directory
            input_file = os.path.join(input_folder, name)
            shutil.copy(os.path.join(upload_folder, filename), input_file)
            
            # Enter file name to db for input
            # TODO: Implement database insertion logic
            
            # Add status - created input true
            file_metadata['status'] = 'created_input'
            
            # Remove uploaded raw files
            os.remove(os.path.join(upload_folder, filename))
            
            # Archive info files into info_archive
            shutil.move(info_file, os.path.join(info_archive_folder, os.path.basename(info_file)))
            
            # Add status ready to process true
            file_metadata['status'] = 'ready_to_process'