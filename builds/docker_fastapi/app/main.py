import logging
from fastapi import FastAPI, Depends, BackgroundTasks
import os
from sqlalchemy.orm import Session  # Add this import
from signalfloweeg.portal.sessionmaker import get_db, drop_all_tables, generate_eeg_format_and_paradigm, generate_database_summary
from signalfloweeg.portal import portal_utils, upload_catalog, import_catalog
from fastapi.middleware.cors import CORSMiddleware

#from process_uploads import process_new_uploads

app = FastAPI()

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

@app.get("/api/clean-uploads")
def clean_uploads():
    logging.info("Cleaning up uploads folder and resetting database...")
    
    # Clean up uploads folder
    UPLOAD_PATH = portal_utils.load_config()['folder_paths']['uploads']
    for filename in os.listdir(UPLOAD_PATH):
        file_path = os.path.join(UPLOAD_PATH, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            logging.error(f"Error deleting file {filename}: {e}")
    
    # Reset database
    drop_all_tables()
    generate_eeg_format_and_paradigm()
    generate_database_summary()
    
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

@app.get("/api/process-uploads")
def process_uploads():
    logging.info("Processing new uploads...")
    UPLOAD_PATH = portal_utils.load_config()['folder_paths']['uploads']
    logging.info(f"UPLOAD_PATH: {UPLOAD_PATH}")
    upload_catalog.process_new_uploads(upload_dir=UPLOAD_PATH)
    import_catalog.update_import_catalog()
    return {"message": "Uploads processed successfully."}

@app.get("/api/get-import-ids")
def get_import_ids():
    logging.info("Getting import IDs...")
    import_ids = import_catalog.get_import_ids()
    return import_ids

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
    #background_tasks.add_task(start_analysis, eeg_file, db)

    #eeg_file = db.query(EEGFile).filter(EEGFile.upload_id == upload_id).first()
    #if not eeg_file:
    #    return {"error": "EEG file not found"}

    # Trigger the analysis process in the background
    #background_tasks.add_task(start_analysis, eeg_file, db)

    return {"message": "Analysis triggered"}



if __name__ == "__main__":
    import uvicorn
    if not os.path.exists("portal_files/logs/"):
        os.makedirs("portal_files/logs/")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", handlers=[logging.FileHandler("portal_files/logs/sf_portal.log"), logging.StreamHandler()])
    uvicorn.run(app, host="0.0.0.0", port=8001)