from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from rich.console import Console
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from rich.console import Console
from rich.table import Table
import json
import yaml
import os
from rich.console import Console

MONGO_URL = "mongodb://localhost:3002"
DATABASE_NAME = "sfportal"

client = AsyncIOMotorClient(MONGO_URL, server_api=ServerApi('1'))
db = client[DATABASE_NAME]
console = Console()

async def get_database():
    return db

async def get_database_url():
    return MONGO_URL

async def is_database_connected():
    try:
        db = await get_database()
        await db.command('ping')
        return True
    except Exception:
        console.print("❌ Failed to connect to the database")
        return False

async def delete_database():
    await client.drop_database(DATABASE_NAME)
    
def initialize_database(reset=False):
    db_url = MONGO_URL
    db_name = "sfportal"  # Set your desired database name
    console = Console()

    console.print(
        "[bold]Initializing or resetting database with the following parameters:[/bold]"
    )
    console.print(f"Database URL: [green]{db_url}[/green]")
    console.print(f"Reset flag: [green]{reset}[/green]")

    client = MongoClient(db_url)

    try:
        # Check if the connection is successful
        client.server_info()
    except ServerSelectionTimeoutError:
        console.print("[bold red]Error: Unable to connect to the MongoDB server.[/bold red]")
        return

    db = client[db_name]

    if reset:
        client.drop_database(db_name)
        console.print(f"Database '{db_name}' dropped successfully.")

    # Create collections based on your models
    collections = [
        "startup", "users", "config", "dataset_catalog", "eeg_formats",
        "eeg_paradigms", "upload_catalog", "import_catalog", "analysis_config",
        "analysis_joblist", "eeg_analyses"
    ]

    for collection_name in collections:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)

    # Verify collections
    table_verification = Table(title="Collection Verification")
    table_verification.add_column("Collection Name", style="cyan")
    table_verification.add_column("Status", style="green")

    for collection_name in collections:
        if collection_name in db.list_collection_names():
            table_verification.add_row(collection_name, "Verified")
        else:
            table_verification.add_row(collection_name, "Not Found")

    console.print(table_verification)

    console.print(f"Database '{db_name}' initialized successfully.")
    
async def check_database_and_tables():
    """
    Verify the presence of required collections in the database.

    Returns:
        bool: True if all required collections are present, otherwise False.
    """
    db = await get_database()
    existing_collections = await db.list_collection_names()

    required_collections = [
        "startup", "config", "upload_catalog", "dataset_catalog", "import_catalog",
        "analysis_joblist", "eeg_paradigms", "eeg_analyses", "eeg_formats", "users"
    ]

    for collection in required_collections:
        if collection not in existing_collections:
            await db.create_collection(collection)
            console.print(f"[yellow]Created missing collection: {collection}[/yellow]")
        else:
            console.print(f"[green]Collection {collection} already exists[/green]")

    return True


async def get_portal_config_path():
    db = await get_database()
    startup_record = await db.startup.find_one({"_id": 1})
    if startup_record:
        return startup_record.get('sf_config_path')
    else:
        return None

async def load_config():
    """
    Load the YAML configuration file.

    Returns:
        dict: The loaded YAML configuration as a dictionary, or None if an error occurs.
    """
    file_path = await get_portal_config_path()

    if not os.path.isfile(file_path):
        file_path = os.path.join(os.path.dirname(__file__), file_path)

    try:
        with open(file_path, "r") as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        console.print(f"File {file_path} not found.")
    except yaml.YAMLError as exc:
        console.print(exc)

async def load_config_from_yaml():
    """
    Load configuration from YAML and update the database accordingly.
    Returns:
        bool: True if successful, False otherwise.
    """
    data = await load_config()
    if data is None:
        return False

    db = await get_database()
    config_collection = db.config

    # Update or insert each section of the configuration
    for section, content in data.items():
        if isinstance(content, list):
            # Handle array content (like users, eeg_formats, etc.)
            section_collection = db[section]
            # Clear existing documents in the collection
            await section_collection.delete_many({})
            # Insert new documents
            if content:
                await section_collection.insert_many(content)
        else:
            # Handle non-array content
            await config_collection.update_one(
                {"_id": section},
                {"$set": content},
                upsert=True
            )

    console.print("[green]Configuration loaded and updated in the database.[/green]")
    return True

async def get_frontend_info():
    """
    Retrieve frontend configuration information from the database.

    Returns:
        dict: Frontend configuration information.
    """
    db = await get_database()
    config_collection = db.config
    frontend_config = await config_collection.find_one({"_id": "frontend"})
    if not frontend_config or 'url' not in frontend_config:
        console.print("[red]Frontend URL not found in configuration. Using default 'http://localhost:5173'.[/red]")
        return {"url": "http://localhost:5173"}
    return frontend_config

async def get_api_info():
    """
    Retrieve API configuration information from the database.

    Returns:
        dict: API configuration information.
    """
    db = await get_database()
    config_collection = db.config
    api_config = await config_collection.find_one({"_id": "api"})
    if not api_config or 'port' not in api_config:
        console.print("[red]API port not found in configuration. Using default port 3005.[/red]")
        return {"port": 3005}
    return api_config

async def get_folder_paths():
    """
    Retrieve folder paths configuration from the database.

    Returns:
        dict: Folder paths configuration information.
    """
    db = await get_database()
    config_doc = await db.config.find_one({"_id": "folder_paths"})
    if config_doc:
        config_doc.pop('_id', None)
        return config_doc
    return {}