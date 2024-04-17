import logging
import os
from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import signalfloweeg.portal as portal
from upload_routes import router as upload_router
from webportal_routes import router as webportal_router
from db_utility_routes import router as utility_router

# Configure logging to output to both the screen and a file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)

config = portal.portal_utils.load_config()

app = FastAPI()
app.include_router(upload_router)
app.include_router(webportal_router)
app.include_router(utility_router)

origins = ["http://localhost:5173"]  # Replace with your JavaScript server's URL

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
@app.on_event("startup")
async def startup_event():
    portal.sessionmaker.get_db()


@app.get("/api/populate_support_tables")
def api_populate_support_tables():
    logging.info("Loading channels and paradigms...")
    portal.models.populate_support_tables()
    return {"message": "Channels and paradigms loaded successfully."}


@app.get("/api/load-database-summary")
def load_database_summary():
    logging.info("Loading database summary...")
    summary = portal.sessionmaker.generate_database_summary()
    return {"message": summary}


@app.get("/api/clean-uploads")
def clean_uploads():
    logging.info("Cleaning up uploads folder and resetting database...")
    from rich.console import Console

    console = Console()
    # Clean up uploads folder
    UPLOAD_PATH = config["folder_paths"]["uploads"]
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

    portal.db.drop_all_tables()
    portal.sessionmaker.generate_eeg_format_and_paradigm()
    portal.sessionmaker.generate_database_summary()

    return {"message": "Uploads folder cleaned and database reset successfully."}


@app.get("/api/request-config")
def request_config():
    logging.info("Processing new uploads...")
    logging.info(config)
    return config


@app.get("/api/get-import-ids")
def get_import_ids():
    logging.info("Getting import IDs...")
    import_ids = portal.import_catalog.get_import_ids()
    return import_ids


@app.get("/api/gen-job-list")
def generate_joblist():
    logging.info("Generating job list...")
    job_list = portal.import_catalog.generate_joblist()
    return job_list


@app.post("/api/trigger_analysis/{upload_id}")
async def trigger_analysis(
    upload_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(portal.sessionmaker.get_db),
):
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title=f"Triggering Analysis for Upload ID: {upload_id}")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta", no_wrap=True)

    import_info = portal.sessionmaker.get_import_info(upload_id)
    if "error" in import_info:
        table.add_row("Error", import_info["error"])
    else:
        for key, value in import_info.items():
            table.add_row(key, str(value))

    console.print(table)

    # Placeholder for background task to start analysis
    return {"message": "Analysis triggered"}


@app.get("/api/show_upload_catalog")
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
    return upload_catalog


@app.get("/api/get-eligible-files")
def list_eligible_files():
    logging.info("Getting eligible files...")
    eligible_files = portal.sessionmaker.get_eligible_files()
    return eligible_files


if __name__ == "__main__":
    import uvicorn

    if not os.path.exists("portal_files/logs/"):
        os.makedirs("portal_files/logs/")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("portal_files/logs/sf_portal.log"),
            logging.StreamHandler(),
        ],
    )
    uvicorn.run(app, host="0.0.0.0", port=8001)
