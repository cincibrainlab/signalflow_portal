import os
import logging
from fastapi import FastAPI
from rich.console import Console
from fastapi.middleware.cors import CORSMiddleware
from routes_main_api import router as main_api_router
from db import get_frontend_info, get_folder_paths, get_api_info
from entrypoint import check_entrypoint, is_startup_table_present
from db import initialize_database
import asyncio
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
console = Console()

app = FastAPI()
app.include_router(main_api_router)

frontend_port = os.environ.get('FRONTEND_PORT', '5173')
origins = [f"http://localhost:{frontend_port}"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



async def run_startup_process():
    restart_database = True
    if restart_database:
        initialize_database()
        if not await check_entrypoint(console):
            console.print("[bold red]Entry point failed.[/bold red]", style="red")
            return False
    else:
        if not await is_startup_table_present():
            initialize_database()

    logger = await set_logging()
    logger.debug("Logging test message from run_startup_process")
    
    await set_cors()
    
    console.print("🎆 [bold cyan]Entry point successful![/bold cyan]")
    return True

async def set_logging():
    # Ensure log directory exists
    folder_paths = await get_folder_paths()
    log_folder = folder_paths["logs"]
    os.makedirs(log_folder, exist_ok=True)

    # Create the log file
    log_file_path = os.path.join(log_folder, "sf_portal.log")
    try:
        with open(log_file_path, 'w') as f:  # Use 'w' to clear the file
            f.write("Log file initialized\n")
        console.print(f"📝 Log file created/accessed: {log_file_path}")
    except IOError as e:
        console.print(f"[bold red]Error creating log file: {e}[/bold red]")
        return

    # Set up logging configuration
    try:
        # Remove any existing handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

        # File handler
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        # Set up the root logger
        logging.root.setLevel(logging.INFO)
        logging.root.addHandler(file_handler)
        logging.root.addHandler(console_handler)

        console.print(f"📝 Logging configured to file: {log_file_path}")
        
        # Test logging
        logging.debug("This is a debug message")
        logging.info("This is an info message")
        logging.warning("This is a warning message")
        logging.error("This is an error message")
        console.print("✅ Test log messages written")
    except Exception as e:
        console.print(f"[bold red]Error setting up logging: {e}[/bold red]")

    # Print file contents to verify
    try:
        with open(log_file_path, 'r') as f:
            content = f.read()
        console.print(f"Log file contents:\n{content}")
    except IOError as e:
        console.print(f"[bold red]Error reading log file: {e}[/bold red]")

    return logging.getLogger()  # Return the logger object for further use

async def set_cors():
    frontend_info = await get_frontend_info()
    origins = [frontend_info["url"], "http://localhost:5173", "http://sf_portal:5173"]
    console.print(f"🌐 [bold cyan]Setting CORS for origins:[/bold cyan] {origins}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logging.info(f"CORS settings updated with origins: {origins}")

async def main():
    try:        
        # Run startup process
        startup_success = await run_startup_process()
        if not startup_success:
            console.print("[bold red]Startup failed. Exiting.[/bold red]", style="red")
            return

        # Get API info after successful startup
        api_info = await get_api_info()
        
        if not api_info or not isinstance(api_info, dict) or "port" not in api_info:
            raise ValueError("Invalid API information")
        
        port = api_info["port"]
        console.print(f"🚀 Starting server on port {port}")
        
        logging.info(f"Starting server on port {port}")  # Add this line
        
        config = uvicorn.Config("main:app", host="0.0.0.0", port=port, reload=True)
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        console.print(f"[bold red]Failed to start the server: {e}[/bold red]", style="red")
        logging.exception("Failed to start the server")  # Add this line
        import traceback
        console.print("[bold yellow]Traceback:[/bold yellow]")
        console.print(traceback.format_exc())

if __name__ == "__main__":
    import uvicorn
    asyncio.run(main())
