import logging
from db import drop_all_tables
from file_operations import add_metadata_to_db
import glob
import os

logging.basicConfig(
    filename='portal_files/logs/eeg_file_catalog.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def check_uploads_folder(folder_path):
    info_files = glob.glob(os.path.join(folder_path, '*.info'))
    return info_files

def ingest_upload_folder(folder_path):
    info_files = check_uploads_folder(folder_path)
    add_metadata_to_db(info_files)

if __name__ == "__main__":
    drop_all_tables()
    ingest_upload_folder(folder_path = './portal_files/uploads/')
