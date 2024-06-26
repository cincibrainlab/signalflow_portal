from fastapi import APIRouter, HTTPException
import logging
import signalfloweeg.portal as portal
import os
from fastapi.responses import JSONResponse
from signalfloweeg.portal.db_connection import is_database_connected

from signalfloweeg.portal.portal_config import (
    get_folder_paths, 
    is_config_table_present
)

from entrypoint import check_entrypoint
from typing import List, Optional
from pydantic import BaseModel

import signalfloweeg as sf

class EEGFormat(BaseModel):
    id: int
    name: str
    description: str

class EEGParadigm(BaseModel):
    id: int
    name: str
    description: str

class Email(BaseModel):
    id: str
    name: str

# Files Tab
class UploadCatalog(BaseModel):
    upload_id: str | None = None
    original_name: str | None = None
    is_set_file: bool | None = None
    has_fdt_file: bool | None = None
    fdt_filename: str | None = None
    fdt_upload_id: str | None = None
    dataset_id: str | None = None
    dataset_name: str | None = None
    eeg_format: str | None = None
    eeg_paradigm: str | None = None
    upload_email: str | None = None
    status: str | None = None
    date_added: str | None = None
    hash: str | None = None
    size: str | None = None
    remove_upload: bool | None = None

class ImportCatalog(BaseModel):
    upload_id: str | None
    original_name: str | None
    is_set_file: bool | None
    has_fdt_file: bool | None
    fdt_filename: str | None
    fdt_upload_id: str | None
    dataset_id: str | None
    dataset_name: str | None
    eeg_format: str | None
    eeg_paradigm: str | None
    upload_email: str | None
    status: str | None
    date_added: str | None
    hash: str | None
    remove_import: bool | None
    sample_rate: int | None
    n_channels: int | None
    n_epochs: int | None
    total_samples: int | None
    mne_load_error: bool | None

class DatasetCatalog(BaseModel):
    dataset_name: str | None
    dataset_id: str | None
    description: str | None


router = APIRouter()

# ────────────────────────────────────────────────────────────────────────────────
# UNIVERSAL TEST
# ────────────────────────────────────────────────────────────────────────────────
@router.get("/api/test")
def test():
    return {"message": "API Test Successful."}

# ────────────────────────────────────────────────────────────────────────────────
# CONFIGURATION CALLS
# ────────────────────────────────────────────────────────────────────────────────
@router.get("/api/get-portal-paths")
def get_portal_paths():
    return {"message": sf.portal.portal_config.get_folder_paths()}

# ────────────────────────────────────────────────────────────────────────────────
# DATABASE: SERVICE UTILITIES
# ────────────────────────────────────────────────────────────────────────────────
  
@router.get("/api/check-db-connection", status_code=200)
def check_database_connection():
    if not is_database_connected():
        raise HTTPException(status_code=503, detail="Database is not connected")
    return {"message": "Database is connected"}

@router.get("/api/delete-database")
def delete_database():
    sf.portal.db_connection.delete_database()
    return {"message": "Database deleted successfully"}

@router.get("/api/load-database-summary")
def load_database_summary():
    logging.info("Loading database summary...")
    summary = sf.portal.db_utilities.generate_database_summary()
    return {"message": summary}

@router.get("/api/reset_portal")
def api_reset_portal():
    logging.info("Resetting portal...")
    logging.info("Cleaning up uploads folder and resetting database...")
    from rich.console import Console

    console = Console()
    # Clean up uploads folder
    if is_config_table_present():
        console.print("ConfigDB table is present. Resetting upload folder...")
        UPLOAD_PATH = get_folder_paths()["uploads"]
        console.print(f"Cleaning up uploads folder: {UPLOAD_PATH}")

        import shutil
        try:
            file_count = 0
            for filename in os.listdir(UPLOAD_PATH):
                file_path = os.path.join(UPLOAD_PATH, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    file_count += 1
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    file_count += 1
            console.print(f"All files in the uploads folder have been removed. Total files deleted: {file_count}")
        except Exception as e:
            console.print(f"Error occurred while deleting files in the uploads folder: {e}")
    portal.models.initialize_database(reset=True)
    check_entrypoint()

    return {"message": "Uploads Removed and Portal Reset Successfully."}

# ────────────────────────────────────────────────────────────────────────────────
# WEBFORMS: UPLOAD TAB
# ────────────────────────────────────────────────────────────────────────────────
@router.get("/api/list-eeg-formats", response_model=List[EEGFormat])
def list_eeg_formats():
    formats = portal.db_webportal.get_eeg_formats()
    logging.debug(f"EEG Formats: {formats}")
    return [EEGFormat(**format) for format in formats]

@router.get("/api/list-eeg-paradigms", response_model=List[EEGParadigm])
def list_eeg_paradigms():
    paradigms = portal.db_webportal.get_eeg_paradigms()
    logging.debug(f"EEG Paradigms: {paradigms}")
    return [EEGParadigm(**paradigm) for paradigm in paradigms]

@router.get("/api/list-emails", response_model=List[Email])
def list_emails():
    emails = portal.db_webportal.get_emails()
    logging.debug(f"Emails: {emails}")
    return [Email(**email) for email in emails]

# ────────────────────────────────────────────────────────────────────────────────
# WEBFORMS: FILES TAB
# ────────────────────────────────────────────────────────────────────────────────
@router.get("/api/get-upload-catalog")
def get_upload_catalog():
    logging.info("Getting file table...")
    file_catalog = portal.db_webportal.get_upload_catalog()
    return [UploadCatalog(**upload) for upload in file_catalog]

@router.get("/api/get-import-catalog")
def get_import_catalog():
    logging.info("Getting import table...")
    import_catalog = portal.db_webportal.get_import_catalog()
    return [ImportCatalog(**import_record) for import_record in import_catalog]

@router.get("/api/get-dataset-catalog")
def get_dataset_catalog():
    logging.info("Getting dataset table...")
    dataset_catalog = portal.db_webportal.get_dataset_catalog()
    return [DatasetCatalog(**dataset) for dataset in dataset_catalog]

@router.get("/api/get-dataset-stats")
def get_dataset_stats():
    logging.info("Getting dataset stats...")
    dataset_stats = portal.db_webportal.get_dataset_stats()
    return dataset_stats

@router.post("/api/merge-datasets")
def merge_datasets(dataset_id1: str, dataset_id2: str):
    try:
        merged_count = portal.db_webportal.merge_two_datasets(dataset_id1, dataset_id2)
        logging.info(f"Merged {merged_count} records from dataset {dataset_id2} into dataset {dataset_id1}")
        return {"success": True, "message": f"Merged {merged_count} records successfully from dataset {dataset_id2} into dataset {dataset_id1}"}
    except Exception as e:
        logging.error(f"Error merging datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ────────────────────────────────────────────────────────────────────────────────
# FUNCTION: DATASET CRUD
# ────────────────────────────────────────────────────────────────────────────────
@router.post("/api/add-dataset", response_model=DatasetCatalog)
def add_dataset(dataset_entry: DatasetCatalog):
    try:
        new_dataset = portal.dataset_catalog.add_dataset(dataset_entry)
        logging.debug(f"New Dataset Added: {new_dataset}")
        return {"success": True, "message": "Dataset added successfully", "dataset": new_dataset}
    except Exception as e:
        logging.error(f"Error adding dataset: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/update-dataset", response_model=DatasetCatalog)
def update_dataset(dataset_entry: DatasetCatalog):
    try:
        updated_dataset = portal.dataset_catalog.update_dataset(dataset_entry)
        logging.debug(f"Dataset Updated: {updated_dataset}")
        print(f"Dataset Updated: {updated_dataset}")
        if updated_dataset:
            return JSONResponse(status_code=200, content={"success": True, "message": "Dataset updated successfully"})
        else:
            return JSONResponse(status_code=404, content={"success": False, "message": "Dataset not found"})
    except Exception as e:
        logging.error(f"Error updating dataset: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ────────────────────────────────────────────────────────────────────────────────
# FUNCTION: UPLOAD PROCESSING
# ────────────────────────────────────────────────────────────────────────────────
@router.get("/api/process-uploads")
def process_uploads():
    logging.info("Processing new uploads...")
    UPLOAD_PATH = portal.portal_config.get_folder_paths()["uploads"]
    logging.info(f"UPLOAD_PATH: {UPLOAD_PATH}")
    portal.upload_catalog.process_new_uploads(upload_dir=UPLOAD_PATH)
    portal.import_catalog.update_import_catalog()
    return {"message": "Uploads processed successfully."}

@router.get("/api/show_upload_catalog")
def list_upload_catalog():
    from rich.console import Console
    from rich.table import Table

    logging.info("Getting Upload Catalog Info")
    upload_catalog = portal.db_webportal.get_upload_catalog()

    console = Console()
    table = Table(title="Upload Catalog")
    table.add_column("Upload_ID", style="cyan", no_wrap=True)
    table.add_column("FDT Upload", style="green", no_wrap=True)
    table.add_column("FileName", style="magenta", no_wrap=True)
    table.add_column("is_set_file", style="green", no_wrap=True)
    table.add_column("has_fdt_file", style="magenta", no_wrap=True)
    table.add_column("fdt_filename", style="green", no_wrap=True)
    for upload in upload_catalog:
        table.add_row(
            upload["upload_id"],
            upload["fdt_id"],
            upload["original_name"],
            str(upload["is_set_file"]),
            str(upload["has_fdt_file"]),
            upload["fdt_filename"],
        )

    console.print(table)
    return [
        {
            "upload_id": upload["upload_id"],
            "fdt_id": upload["fdt_id"],
            "original_name": upload["original_name"],
            "is_set_file": upload["is_set_file"],
            "has_fdt_file": upload["has_fdt_file"],
            "fdt_filename": upload["fdt_filename"],
        }
        for upload in upload_catalog
    ]


## Legacy code

class DatasetCreate(BaseModel):
    dataset_name: str
    description: str
    eeg_format_name: Optional[str] = None
    eeg_paradigm_name: Optional[str] = None

@router.get("/api/list-datasets", response_model=List[DatasetCatalog])
def list_datasets():
    datasets = portal.dataset_catalog.get_info()
    logging.debug(f"Datasets: {datasets}")
    return [DatasetCatalog(**dataset) for dataset in datasets]

def main():
    from rich.console import Console
    from rich.prompt import Prompt
    import subprocess

    console = Console()

    port_number = 3005
    api_base_url = f"http://localhost:{port_number}/api"
    api_commands = {
        "0": {
            "description": "Universal Test API",
            "command": f"curl {api_base_url}/test",
            "prompts": [],
        },
        "1": {
            "description": "Load Database Summary",
            "command": f"curl {api_base_url}/load-database-summary",
            "prompts": [],
        },
    }
    while True:
        console.clear()
        console.print("SignalFlow Portal API Menu", style="bold green")
        for choice, command in api_commands.items():
            console.print(f"{choice}. {command['description']}")
        console.print("q. Exit")

        choice = Prompt.ask("Enter your choice (or 'q' to quit)", choices=list(api_commands.keys()) + ['q'])

        if choice == 'q':
            break

        if api_commands[choice]["command"]:
            prompts = api_commands[choice]["prompts"]
            command_args = {}
            for prompt in prompts:
                command_args[prompt.split()[-1].lower()] = Prompt.ask(prompt)

            command = api_commands[choice]["command"].format(**command_args)
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            console.print(result.stdout)
            console.print("API command executed. Press any key to return to the menu...")
            input()  # Wait for user input before continuing
            
if __name__ == "__main__":
    main()
