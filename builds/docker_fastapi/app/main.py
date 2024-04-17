import logging
import os
from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from rich.console import Console

from upload_routes import router as upload_router
from webportal_routes import router as webportal_router
from db_utility_routes import router as utility_router
from reports_routes import router as report_router
from jobs_routes import router as jobs_router

from signalfloweeg.portal.models import initialize_database
from signalfloweeg.portal.portal_config import load_config_from_yaml, get_folder_paths, get_frontend_info

console = Console()

app = FastAPI()
app.include_router(upload_router)
app.include_router(webportal_router)
app.include_router(utility_router)
app.include_router(report_router)
app.include_router(jobs_router)



origins = [get_frontend_info()["url"]]  # Replace with your JavaScript server's URL

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database Setup
def startup_event():
    console.print("[bold green]SignalFlow Portal Starting ...![/bold green]")
    initialize_database(reset=True)
    load_config_from_yaml()

@app.get("/")
def read_root():
    return FileResponse('/docs')

if __name__ == "__main__":
    startup_event()

    import uvicorn

    LOG_FOLDER = get_folder_paths()["logs"]

    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

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
