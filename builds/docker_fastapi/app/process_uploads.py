import logging
import glob
import os
from db import drop_all_tables
from portal_utils import load_config
from upload_catalog import update_upload_catalog
from import_catalog import update_import_catalog

def find_info_files(upload_dir):
    info_files = glob.glob(os.path.join(upload_dir, "*.info"))
    logging.info(f"Detected {len(info_files)} .info files in {upload_dir}.")
    return info_files

def process_new_uploads(upload_dir):
    logging.info(f"Scanning upload directory: {upload_dir}")
    info_files = find_info_files(upload_dir)
    update_upload_catalog(info_files)
    update_import_catalog()
    logging.info("Upload and import catalogs updated.")
