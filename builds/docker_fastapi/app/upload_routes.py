from fastapi import APIRouter, Depends, BackgroundTasks
import logging
from signalfloweeg.portal import portal_utils, upload_catalog

router = APIRouter()


@router.get("/api/process-uploads")
def process_uploads():
    logging.info("Processing new uploads...")
    UPLOAD_PATH = portal_utils.load_config()["folder_paths"]["uploads"]
    logging.info(f"UPLOAD_PATH: {UPLOAD_PATH}")
    upload_catalog.process_new_uploads(upload_dir=UPLOAD_PATH)
    # import_catalog.update_import_catalog()
    return {"message": "Uploads processed successfully."}


# Add more upload-related endpoints here
