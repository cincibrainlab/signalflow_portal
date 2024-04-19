import os
import logging
import signal
from fastapi import FastAPI
from rich.console import Console
from fastapi.middleware.cors import CORSMiddleware

from signalfloweeg.portal.portal_config import (
    set_portal_config_path,
    get_portal_config_path,
    get_frontend_info,
    get_folder_paths,
    get_api_info,
)

from routes_upload_form import router as upload_form_router

#from upload_routes import router as upload_router
#from webportal_routes import router as webportal_router
#from reports_routes import router as report_router
#from jobs_routes import router as jobs_router

console = Console()


# Setup the portal_config.yaml path
def update_portal_config():
    console.print("[bold green]SignalFlow Portal Starting ...![/bold green]")
    current_directory = os.getcwd()
    set_portal_config_path(os.path.join(current_directory, "portal_config.yaml"))
    return get_portal_config_path()

update_portal_config()


app = FastAPI()
app.include_router(upload_form_router)
#app.include_router(webportal_router)
#app.include_router(report_router)
#app.include_router(jobs_router)


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

LOG_FOLDER = get_folder_paths()["logs"]
logging.info("Starting SignalFlow Portal ...")
logging.info(f"Log folder: {LOG_FOLDER}")

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

log_file_path = os.path.join(LOG_FOLDER, "sf_portal.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler(),
    ],
)
print(f"Logging to file: {log_file_path}")
def signal_handler(signum, frame):
    logging.info("Signal received: {}, initiating graceful shutdown.".format(signum))
    # Perform any necessary cleanup here
    logging.info("Cleanup completed, shutting down.")
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)




if __name__ == "__main__":

    import uvicorn

    try:
        port = get_api_info()["port"]
        uvicorn.run(app, host="0.0.0.0", port=port)
        logging.info(f"Uvicorn running on http://0.0.0.0:{port} (Press CTRL+C to quit)")
    except KeyError:
        logging.error("API port configuration is missing.")
    except Exception as e:
        logging.error(f"Failed to start the server: {e}")
