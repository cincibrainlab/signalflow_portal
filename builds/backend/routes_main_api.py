from fastapi import APIRouter, HTTPException
import logging

import db as flow_db
import os
from fastapi.responses import JSONResponse
from flows.AnalysisFlow import AnalysisFlow

from entrypoint import check_entrypoint
from typing import List
import models





router = APIRouter()

# ────────────────────────────────────────────────────────────────────────────────
# UNIVERSAL TEST
# ────────────────────────────────────────────────────────────────────────────────
@router.get("/api/test")
async def test():
    return {"message": "API Test Successful."}

# ────────────────────────────────────────────────────────────────────────────────
# CONFIGURATION CALLS
# ───────────────────────────────────────────────────────────────────────���────────
@router.get("/api/get-portal-paths")
async def get_portal_paths():
    paths = await flow_db.get_folder_paths()
    return {"message": paths}

# ────────────────────────────────────────────────────────────────────────────────
# DATABASE: SERVICE UTILITIES
# ────────────────────────────────────────────────────────────────────────────────
  
@router.get("/api/check-db-connection", status_code=200)
async def check_database_connection():
    if not await flow_db.is_database_connected():
        raise HTTPException(status_code=503, detail="Database is not connected")
    return {"message": "Database is connected"}

@router.get("/api/delete-database")
async def delete_database():
    await flow_db.delete_database()
    return {"message": "Database deleted successfully"}

@router.get("/api/load-database-summary")
async def load_database_summary():
    logging.info("Loading database summary...")
    summary = await flow_db.generate_database_summary()
    return {"message": summary}

@router.get("/api/reset_portal")
async def api_reset_portal():
    logging.info("Resetting portal...")
    logging.info("Cleaning up uploads folder and resetting database...")
    from rich.console import Console

    console = Console()
    # Clean up uploads folder
    if await flow_db.is_config_table_present():
        console.print("ConfigDB table is present. Resetting upload folder...")
        UPLOAD_PATH = (await flow_db.get_folder_paths())["uploads"]
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
    await flow_db.initialize_database(reset=True)
    await check_entrypoint(console)

    return {"message": "Uploads Removed and Portal Reset Successfully."}

# ────────────────────────────────────────────────────────────────────────────────
# WEBFORMS: UPLOAD TAB
# ────────────────────────────────────────────────────────────────────────────────
@router.get("/api/list-eeg-formats", response_model=List[models.EEGFormat])
async def list_eeg_formats():
    formats = await flow_db.get_eeg_formats()
    logging.debug(f"EEG Formats: {formats}")
    return [models.EEGFormat(**format) for format in formats]

@router.get("/api/list-eeg-paradigms", response_model=List[models.EEGParadigm])
async def list_eeg_paradigms():
    paradigms = await flow_db.get_eeg_paradigms()
    logging.debug(f"EEG Paradigms: {paradigms}")
    return [models.EEGParadigm(**paradigm) for paradigm in paradigms]

# ────────────────────────────────────────────────────────────────────────────────
# WEBFORMS: FILES TAB
# ────────────────────────────────────────────────────────────────────────────────
@router.get("/api/get-upload-catalog")
async def get_upload_catalog():
    logging.info("Getting file table...")
    file_catalog = await flow_db.get_upload_catalog()
    return [models.UploadCatalog(**upload) for upload in file_catalog]

@router.get("/api/get-import-catalog")
async def get_import_catalog():
    logging.info("Getting import table...")
    import_catalog = await flow_db.get_import_catalog()
    return [models.ImportCatalog(**import_record) for import_record in import_catalog]

@router.get("/api/get-dataset-catalog")
async def get_dataset_catalog():
    logging.info("Getting dataset table...")
    dataset_catalog = await flow_db.get_dataset_catalog()
    return [models.DatasetCatalog(**dataset) for dataset in dataset_catalog]

@router.get("/api/get-dataset-stats")
async def get_dataset_stats():
    logging.info("Getting dataset stats...")
    dataset_stats = await flow_db.get_dataset_stats()
    return dataset_stats

@router.post("/api/merge-datasets")
async def merge_datasets(dataset_id1: str, dataset_id2: str):
    try:
        merged_count = await flow_db.merge_datasets(dataset_id1, dataset_id2)
        logging.info(f"Merged {merged_count} records from dataset {dataset_id2} into dataset {dataset_id1}")
        return {"success": True, "message": f"Merged {merged_count} records successfully from dataset {dataset_id2} into dataset {dataset_id1}"}
    except Exception as e:
        logging.error(f"Error merging datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ────────────────────────────────────────────────────────────────────────────────
# FUNCTION: DATASET CRUD
# ───────────────────────────────────────────────────────────────────────────────���
@router.post("/api/add-dataset", response_model=models.DatasetCatalog)
async def add_dataset(dataset_entry: models.DatasetCatalog):
    try:
        new_dataset = await flow_db.add_dataset(dataset_entry)
        logging.debug(f"New Dataset Added: {new_dataset}")
        return {"success": True, "message": "Dataset added successfully", "dataset": new_dataset}
    except Exception as e:
        logging.error(f"Error adding dataset: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/update-dataset", response_model=models.DatasetCatalog)
async def update_dataset(dataset_entry: models.DatasetCatalog):
    try:
        updated_dataset = await flow_db.update_dataset(dataset_entry)
        logging.debug(f"Dataset Updated: {updated_dataset}")
        print(f"Dataset Updated: {updated_dataset}")
        if updated_dataset:
            return JSONResponse(status_code=200, content={"success": True, "message": "Dataset updated successfully"})
        else:
            return JSONResponse(status_code=404, content={"success": False, "message": "Dataset not found"})
    except Exception as e:
        logging.error(f"Error updating dataset: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ────────────────���───────────────────────────────────────────────────────────────
# FUNCTION: UPLOAD PROCESSING
# ────────────────────────────────────────────────────────────────────────────────
@router.get("/api/process-uploads")
async def process_uploads():
    logging.info("Processing new uploads...")
    UPLOAD_PATH = (await flow_db.get_folder_paths())["uploads"]
    logging.info(f"UPLOAD_PATH: {UPLOAD_PATH}")
    await flow_db.process_new_uploads(upload_dir=UPLOAD_PATH)
    await flow_db.update_import_catalog()
    return {"message": "Uploads processed successfully."}

@router.get("/api/show_upload_catalog")
async def list_upload_catalog():
    from rich.console import Console
    from rich.table import Table

    logging.info("Getting Upload Catalog Info")
    upload_catalog = await flow_db.get_upload_catalog()

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

# ────────────────────────────────────────────────────────────────────────────────
# FUNCTION: ANALYSIS ENDPOINT
# ─────────────────────���──────────────────────────────────────────────────────────
@router.get("/api/run-analysis")
async def schedule_analysis(filename: str):
    await AnalysisFlow(filename=filename)
    return {"message": f"Analysis scheduled for file: {filename}"}

## Legacy code


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
