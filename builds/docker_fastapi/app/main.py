import os
import logging
from fastapi import FastAPI
from rich.console import Console
from fastapi.middleware.cors import CORSMiddleware

from signalfloweeg.portal.portal_config import (
    set_portal_config_path,
    get_portal_config_path,
    get_frontend_info,
    initialize_database,
    get_folder_paths,
    get_api_info,
)

from upload_routes import router as upload_router
from webportal_routes import router as webportal_router
from reports_routes import router as report_router
from jobs_routes import router as jobs_router

console = Console()


# Setup the portal_config.yaml path
def update_portal_config():
    console.print("[bold green]SignalFlow Portal Starting ...![/bold green]")
    current_directory = os.getcwd()
    set_portal_config_path(os.path.join(current_directory, "portal_config.yaml"))
    return get_portal_config_path()


initialize_database(reset=False)
update_portal_config()


app = FastAPI()
app.include_router(upload_router)
app.include_router(webportal_router)
app.include_router(report_router)
app.include_router(jobs_router)


def set_cors():
    origins = [get_frontend_info()["url"]]  # Replace with your JavaScript server's URL
    console.print(f"[bold cyan]Setting CORS for origins:[/bold cyan] {origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logging.info(f"CORS settings applied with origins: {origins}")


set_cors()


if __name__ == "__main__":
    LOG_FOLDER = get_folder_paths()["logs"]
    logging.info("Starting SignalFlow Portal ...")

    import uvicorn

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

    try:
        port = get_api_info()["port"]
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
        logging.info(f"Uvicorn running on http://0.0.0.0:{port} (Press CTRL+C to quit)")
    except KeyError:
        logging.error("API port configuration is missing.")
    except Exception as e:
        logging.error(f"Failed to start the server: {e}")
