from fastapi import APIRouter
import logging
import os
from signalfloweeg.portal import upload_catalog
from signalfloweeg.portal.portal_config import get_folder_paths, load_config, is_config_table_present
from signalfloweeg.portal.models import initialize_database
from signalfloweeg.portal.db_utilities import generate_database_summary


router = APIRouter()


@router.get("/api/process-uploads")
def process_uploads():
    logging.info("Processing new uploads...")
    UPLOAD_PATH = get_folder_paths()["uploads"]
    logging.info(f"UPLOAD_PATH: {UPLOAD_PATH}")
    upload_catalog.process_new_uploads(upload_dir=UPLOAD_PATH)
    # import_catalog.update_import_catalog()
    return {"message": "Uploads processed successfully."}


@router.get("/api/reset_portal")
def api_reset_portal():
    logging.info("Resetting portal...")
    logging.info("Cleaning up uploads folder and resetting database...")
    from rich.console import Console

    console = Console()
    # Clean up uploads folder
    if is_config_table_present():
        console.print("ConfigDB table is present. Rseetting upload folder...")
        UPLOAD_PATH = get_folder_paths()["uploads"]
        console.print(f"Cleaning up uploads folder: {UPLOAD_PATH}")

        import shutil

        try:
            for filename in os.listdir(UPLOAD_PATH):
                file_path = os.path.join(UPLOAD_PATH, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            console.print("All files in the uploads folder have been removed.")
        except Exception as e:
            console.print(f"Error occurred while deleting files in the uploads folder: {e}")

    initialize_database(reset=True)
    generate_database_summary()

    return {"message": "Uploads Removed and Portal Reset Successfully."}

if __name__ == "__main__":
    api_reset_portal()

