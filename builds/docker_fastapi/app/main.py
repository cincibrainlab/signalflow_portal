import logging
from fastapi import FastAPI, Depends, BackgroundTasks
import os
from sqlalchemy.orm import Session  # Add this import
from signalfloweeg.portal.sessionmaker import (
    get_db, drop_all_tables,
    generate_eeg_format_and_paradigm,
    generate_database_summary,
    get_eeg_formats,
    get_eeg_paradigms,
    get_dataset_info,
    get_eligible_files,
    get_upload_catalog
)
from signalfloweeg.portal import portal_utils, upload_catalog, import_catalog
from fastapi.middleware.cors import CORSMiddleware

# Revision

from .upload_routes import router as upload_router



app = FastAPI()
app.include_router(upload_router)

origins = ["http://localhost:1234"]  # Replace with your JavaScript server's URL

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/test")
def test(db: Session = Depends(get_db)):
    return {"message": "Hello World"}


@app.get("/api/drop-tables")
def api_drop_all_tables():
    drop_all_tables()
    return {"message": "DB tables dropped successfully."}


@app.get("/api/load-channels-paradigms")
def load_channels_paradigms():
    logging.info("Loading channels and paradigms...")
    generate_eeg_format_and_paradigm()
    return {"message": "Channels and paradigms loaded successfully."}


@app.get("/api/load-database-summary")
def load_database_summary():
    logging.info("Loading database summary...")
    summary = generate_database_summary()
    return {"message": summary}


@app.get("/api/clean-uploads")
def clean_uploads():
    logging.info("Cleaning up uploads folder and resetting database...")
    from rich.console import Console
    console = Console()
    # Clean up uploads folder
    UPLOAD_PATH = portal_utils.load_config()['folder_paths']['uploads']
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

    drop_all_tables()
    generate_eeg_format_and_paradigm()
    generate_database_summary()

    return {"message": "Uploads folder cleaned and database reset successfully."}

    return {"message": "Uploads folder cleaned and database reset successfully."}


# @app.get("/api/drop-tables")
# def db_drop_all_tables():
#     logging.info("Processing new uploads...")
#     db.drop_all_tables()
#     return {"message": "DB tables dropped successfully."}

@app.get("/api/request-config")
def request_config():
    logging.info("Processing new uploads...")
    config = portal_utils.load_config()
    logging.info(config)
    return config


@app.get("/api/list-eeg-formats")
def list_eeg_formats():
    return get_eeg_formats()


@app.get("/api/list-eeg-paradigms")
def list_eeg_paradigms():
    return get_eeg_paradigms()




@app.get("/api/get-import-ids")
def get_import_ids():
    logging.info("Getting import IDs...")
    import_ids = import_catalog.get_import_ids()
    return import_ids


@app.get("/api/gen-job-list")
def generate_joblist():
    logging.info("Generating job list...")
    job_list = import_catalog.generate_joblist()
    return job_list


@app.post("/api/trigger_analysis/{upload_id}")
async def trigger_analysis(upload_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    from rich.console import Console
    from rich.table import Table
    from signalfloweeg.portal.sessionmaker import get_import_info

    console = Console()
    table = Table(title=f"Triggering Analysis for Upload ID: {upload_id}")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta", no_wrap=True)

    import_info = get_import_info(upload_id)
    if "error" in import_info:
        table.add_row("Error", import_info["error"])
    else:
        for key, value in import_info.items():
            table.add_row(key, str(value))

    console.print(table)

    # Trigger the analysis process in the background
    # background_tasks.add_task(start_analysis, eeg_file, db)

    # eeg_file = db.query(EEGFile).filter(EEGFile.upload_id == upload_id).first()
    # if not eeg_file:
    #    return {"error": "EEG file not found"}

    # Trigger the analysis process in the background
    # background_tasks.add_task(start_analysis, eeg_file, db)

    return {"message": "Analysis triggered"}

@app.get("/api/show_upload_catalog")
def list_upload_catalog():
    from rich.console import Console
    from rich.table import Table

    logging.info("Getting Upload Catalog Info")
    upload_catalog = get_upload_catalog()

    console = Console()
    table = Table(title="Upload Catalog")
    table.add_column("Upload_ID", style="cyan", no_wrap=True)
    table.add_column("FDT Upload", style="green", no_wrap=True)
    table.add_column("FileName", style="magenta", no_wrap=True)
    table.add_column("is_set_file", style="green", no_wrap=True)
    table.add_column("has_fdt_file", style="magenta", no_wrap=True)
    table.add_column("fdt_filename", style="green", no_wrap=True)
    for upload in upload_catalog:
        table.add_row(upload["upload_id"],upload["fdt_id"],  upload["original_name"], 
            str(upload["is_set_file"]), str(upload["has_fdt_file"]), upload["fdt_filename"])

    console.print(table)
    return upload_catalog


@app.get("/api/get-dataset-info")
def list_dataset_info():
    from rich.console import Console
    from rich.table import Table

    logging.info("Getting dataset information...")
    dataset_info = get_dataset_info()

    console = Console()
    table = Table(title="Dataset Information")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta", no_wrap=True)
    table.add_column("Description", style="green", no_wrap=True)
    table.add_column("EEG Format ID", style="yellow", no_wrap=True)
    table.add_column("EEG Paradigm ID", style="blue", no_wrap=True)
    for dataset in dataset_info:
        table.add_row(dataset["dataset_id"], dataset["dataset_name"], dataset["description"],
                      dataset["eeg_format"], dataset["eeg_paradigm"])

    console.print(table)
    # console.print(dataset_info)
    return dataset_info


@app.get("/api/get-eligible-files")
def list_eligible_files():
    logging.info("Getting eligible files...")
    eligible_files = get_eligible_files()
    return eligible_files


if __name__ == "__main__":
    import uvicorn

    if not os.path.exists("portal_files/logs/"):
        os.makedirs("portal_files/logs/")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[logging.FileHandler("portal_files/logs/sf_portal.log"), logging.StreamHandler()])
    uvicorn.run(app, host="0.0.0.0", port=8001)
