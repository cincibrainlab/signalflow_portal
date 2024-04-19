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

@router.post("/api/add-dataset", response_model=dict)
def add_dataset(dataset: DatasetCreate):
    try:
        new_dataset = portal.db_datasets.add_record(dataset.dataset_name, dataset.description, dataset.eeg_format_id, dataset.eeg_paradigm_id)
        logging.debug(f"New Dataset Added: {new_dataset}")
        return {"success": True, "message": "Dataset added successfully", "dataset": new_dataset}
    except Exception as e:
        logging.error(f"Error adding dataset: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/list-emails", response_model=List[Email])
def list_emails():
    emails = portal.db_webportal.get_emails()
    logging.debug(f"Emails: {emails}")
    return [Email(**email) for email in emails]