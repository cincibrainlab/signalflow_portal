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
origins = [f"http://localhost:{frontend_port}", f"http://172.22.0.2:{frontend_port}/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



async def run_startup_process():
    restart_database = False
    if restart_database:
        initialize_database()
        if not await check_entrypoint(console):
            console.print("[bold red]Entry point failed.[/bold red]", style="red")
            return False
    else:
        if not await is_startup_table_present():
            initialize_database()

    await set_logging()
    await set_cors()
    
    console.print("🎆 [bold cyan]Entry point successful![/bold cyan]")
    return True

async def set_logging():
    # Ensure log directory exists
    folder_paths = await get_folder_paths()
    log_folder = folder_paths["logs"]
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
        
        config = uvicorn.Config("main:app", host="0.0.0.0", port=port, reload=True)
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        console.print(f"[bold red]Failed to start the server: {e}[/bold red]", style="red")
        import traceback
        console.print("[bold yellow]Traceback:[/bold yellow]")
        console.print(traceback.format_exc())

if __name__ == "__main__":
    import uvicorn
    asyncio.run(main())
