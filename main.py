import logging
import glob
import os

from db import drop_all_tables
from upload_catalog import update_upload_catalog
from import_catalog import update_import_catalog
from portal_utils import load_config

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", handlers=[logging.FileHandler("portal_files/logs/eeg_file_catalog.log"), logging.StreamHandler()])

# Load configuration
config = load_config()
UPLOAD_PATH = config['folder_paths']['uploads']

# Function to process new uploads
def process_new_uploads(upload_dir=UPLOAD_PATH):
    logging.info(f"Scanning upload directory: {upload_dir}")
    def find_info_files(upload_dir):
        info_files = glob.glob(os.path.join(upload_dir, "*.info"))
        logging.info(f"Detected {len(info_files)} .info files in {upload_dir}.")
        return info_files
    update_upload_catalog(find_info_files(upload_dir))
    logging.info("Upload directory processing complete.")

# Main execution
if __name__ == "__main__":
    drop_all_tables()
    process_new_uploads(upload_dir=UPLOAD_PATH)
    update_import_catalog()
