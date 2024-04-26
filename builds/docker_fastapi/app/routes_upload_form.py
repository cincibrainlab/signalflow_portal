from fastapi import APIRouter, HTTPException
import logging
import signalfloweeg.portal as portal

from typing import List, Optional
from pydantic import BaseModel

class EEGFormat(BaseModel):
    id: int
    name: str
    description: str

class EEGParadigm(BaseModel):
    id: int
    name: str
    description: str

class Dataset(BaseModel):
    id: str
    name: str
    description: str
    eeg_format: Optional[str] = None
    eeg_paradigm: Optional[str] = None

class DatasetCreate(BaseModel):
    dataset_name: str
    description: str
    eeg_format_name: Optional[str] = None
    eeg_paradigm_name: Optional[str] = None

class Email(BaseModel):
    id: str
    name: str


router = APIRouter()

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

@router.get("/api/list-datasets", response_model=List[Dataset])
def list_datasets():
    datasets = portal.db_datasets.get_info()
    logging.debug(f"Datasets: {datasets}")
    return [Dataset(**dataset) for dataset in datasets]

@router.get("/api/list-emails", response_model=List[Email])
def list_emails():
    emails = portal.db_webportal.get_emails()
    logging.debug(f"Emails: {emails}")
    return [Email(**email) for email in emails]

@router.get("/api/process-uploads")
def process_uploads():
    logging.info("Processing new uploads...")
    UPLOAD_PATH = portal.portal_config.get_folder_paths()["uploads"]
    logging.info(f"UPLOAD_PATH: {UPLOAD_PATH}")
    portal.upload_catalog.process_new_uploads(upload_dir=UPLOAD_PATH)
    # import_catalog.update_import_catalog()
    return {"message": "Uploads processed successfully."}


@router.get("/api/show_upload_catalog")
def list_upload_catalog():
    from rich.console import Console
    from rich.table import Table

    logging.info("Getting Upload Catalog Info")
    upload_catalog = portal.sessionmaker.get_upload_catalog()

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

@router.post("/api/add-dataset", response_model=dict)
def add_dataset(dataset: DatasetCreate):
    try:
        new_dataset = portal.db_datasets.add_record(dataset.dataset_name, dataset.description, dataset.eeg_format_id, dataset.eeg_paradigm_id)
        logging.debug(f"New Dataset Added: {new_dataset}")
        return {"success": True, "message": "Dataset added successfully", "dataset": new_dataset}
    except Exception as e:
        logging.error(f"Error adding dataset: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
