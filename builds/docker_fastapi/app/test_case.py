import logging
from fastapi import FastAPI
import os
from signalfloweeg.portal import portal_utils, db, upload_catalog, import_catalog
from fastapi.middleware.cors import CORSMiddleware

logging.info("Processing new uploads...")
UPLOAD_PATH = portal_utils.load_config()['folder_paths']['uploads']
logging.info(f"UPLOAD_PATH: {UPLOAD_PATH}")
upload_catalog.process_new_uploads(upload_dir=UPLOAD_PATH)
import_catalog.update_import_catalog()