import os
import sys
import logging
from fastapi import FastAPI
from rich.console import Console
from fastapi.middleware.cors import CORSMiddleware
from api.routes_main_api import router as main_api_router
from signalfloweeg.portal.portal_config import (
    get_frontend_info, get_folder_paths, get_api_info
)
from entrypoint import entry_point

"""
Program Flow Diagram:

+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|   entry_point    +---->+   set_logging    +---->+     set_cors     |
|                  |     |                  |     |                  |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         |                        |                        |
         v                        v                        v
+--------+---------+     +--------+---------+     +--------+---------+
|                  |     |                  |     |                  |
|  Database Check  |     |  Logging Setup   |     |  CORS Setup      |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+

Description:
1. The program starts by checking the database connection and configuration through `entry_point`.
2. If successful, it proceeds to set up logging via `set_logging`.
3. Finally, it configures CORS settings with `set_cors` to allow cross-origin requests.
"""


app = FastAPI()
app.include_router(main_api_router)


if entry_point():
    console = Console()
    console.print("🎆 [bold cyan]Entry point successful![/bold cyan]")
    
    def set_logging():

        # Ensure log directory exists
        log_folder = get_folder_paths()["logs"]
        os.makedirs(log_folder, exist_ok=True)

        # Set up logging configuration
        log_file_path = os.path.join(log_folder, "sf_portal.log")
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logging.FileHandler(log_file_path)],
        )
        console.print(f"📝 Logging to file: {log_file_path}")

    def set_cors():
        origins = [
            get_frontend_info()["url"]
        ]  # Replace with your JavaScript server's URL
        console.print(f"🌐 [bold cyan]Setting CORS for origins:[/bold cyan] {origins}")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logging.info(f"CORS settings applied with origins: {origins}")
    set_logging()    
    set_cors()
else:
    console.print("[bold red]Entry point failed.[/bold red]", style="red")
    sys.exit(1)




if __name__ == "__main__":
    import uvicorn
    try:
        port = get_api_info()["port"]
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
        logging.info(f"Uvicorn running on http://0.0.0.0:{port} (Press CTRL+C to quit)")
    except KeyError:
        console.print("[bold red]API port configuration is missing.[/bold red]", style="red")
    except Exception as e:
        console.print(f"[bold red]Failed to start the server: {e}[/bold red]", style="red")

