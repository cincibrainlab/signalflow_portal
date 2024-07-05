import os
import asyncio
from signalfloweeg.portal.db_connection import is_database_connected, get_database
from signalfloweeg.portal.models import Startup, initialize_database
from signalfloweeg.portal.portal_config import (
    check_database_and_tables, 
    load_config_from_yaml
)
from rich.console import Console

console = Console()

async def is_startup_table_present():
    db = await get_database()
    collections = await db.list_collection_names()
    return 'startup' in collections

async def reset_database():
    db = await get_database()
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].drop()
    console.print("✅ Database reset complete")

async def add_portal_config_path(portal_config_path):
    try:
        db = await get_database()
        startup_collection = db.startup
        await startup_collection.update_one(
            {"_id": 1},
            {"$set": {"sf_config_path": portal_config_path}},
            upsert=True
        )
        console.print(f"✅ Startup collection updated with portal config path: {portal_config_path}")
        return True
    except Exception as e:
        console.print(f"❌ Failed to update startup collection: {e}")
        return False

def free_disk_space(target_path):
    """
    Function to check if the free disk space in a given path is greater than 10 GB
    :param target_path: The path to check the free disk space
    :return: True if the free disk space is greater than 10 GB, False otherwise
    """
    import shutil
    total, used, free = shutil.disk_usage(target_path)
    return (free // (2**30)) > 10  # Convert bytes to gigabytes and check if greater than 10 GB

async def check_entrypoint(console: Console):
    console.print("🚀 [bold magenta]Entrypoint Checks:[/bold magenta]", style="bold on blue")
    entrypoint_check = dict()
    
    # check if database is connected
    entrypoint_check['database_connected'] = await is_database_connected()
    status_icon = '✅' if entrypoint_check['database_connected'] else '❌'
    console.print(f"[bold]{status_icon} Database Connected:[/bold] [yellow]{entrypoint_check['database_connected']}[/yellow]")
    if not entrypoint_check['database_connected']:
        return False
    
    # Add the portal config path to the database
    portal_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portal_config.yaml')
    entrypoint_check['portal_config_path'] = await add_portal_config_path(portal_config_path)
    status_icon = '✅' if entrypoint_check['portal_config_path'] else '❌'
    console.print(f"[bold]{status_icon} Portal Config Path Assigned:[/bold] [yellow]{portal_config_path}[/yellow]")
   
    # check if the database and tables are present
    entrypoint_check['database_and_tables'] = await check_database_and_tables()
    status_icon = '✅' if entrypoint_check['database_and_tables'] else '❌'
    console.print(f"[bold]{status_icon} Database Tables Validated:[/bold] [yellow]{entrypoint_check['database_and_tables']}[/yellow]")
  
    # check if portal_config.yaml is loaded
    entrypoint_check['config_loaded'] = await load_config_from_yaml()
    status_icon = '✅' if entrypoint_check['config_loaded'] else '❌'
    console.print(f"[bold]{status_icon} Portal Config Loaded:[/bold] [yellow]{entrypoint_check['config_loaded']}[/yellow]")
   
    # check if free disk space is greater than 10 GB
    entrypoint_check['disk_space'] = free_disk_space(portal_config_path)
    status_icon = '✅' if entrypoint_check['disk_space'] else '❌'
    console.print(f"[bold]{status_icon} Free Disk Space Check (> 10 GB):[/bold] [yellow]{entrypoint_check['disk_space']}[/yellow]")

    all_checks_passed = all(entrypoint_check.values())
    return all_checks_passed

if __name__ == "__main__":
    valid_entry = asyncio.run(check_entrypoint())
