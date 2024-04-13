from fastapi import APIRouter
import logging
from signalfloweeg.portal.db_webportal import (
    get_eeg_formats, 
    get_eeg_paradigms
    )
from signalfloweeg.portal.db_datasets import (
    get_dataset_info
)

router = APIRouter()


# Add more upload-related endpoints here
@router.get("/api/list-eeg-formats")
def list_eeg_formats():
    formats = get_eeg_formats()
    logging.debug(f"EEG Formats: {formats}")
    return formats

@router.get("/api/list-eeg-paradigms")
def list_eeg_paradigms():
    paradigms = get_eeg_paradigms()
    logging.debug(f"EEG Paradigms: {paradigms}")
    return paradigms

@router.get("/api/list-datasets")
def list_datasets():
    datasets = get_dataset_info()
    simplified_datasets = [{"id": dataset["id"], "name": dataset["name"], "description": dataset["description"]} for dataset in datasets]
    logging.debug(f"Simplified Datasets: {simplified_datasets}")
    return simplified_datasets

