from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from rich.console import Console
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from rich.table import Table
import yaml
import os
import logging
import json
import datetime
from shutil import move
import glob
import hashlib
from shutil import copy
import mne
import models
from bson import ObjectId
import asyncio

DB_PORT = int(os.environ.get('DB_PORT', '3002'))
MONGO_URL = f"mongodb://localhost:{DB_PORT}"
DATABASE_NAME = "sfportal"

client = AsyncIOMotorClient(MONGO_URL, server_api=ServerApi('1'))
db = client[DATABASE_NAME]
console = Console()
global config

async def get_database():
    client = AsyncIOMotorClient(MONGO_URL, server_api=ServerApi('1'))
    curr_db = client[DATABASE_NAME]
    return curr_db

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
    
def initialize_database(reset=True):
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
        "Participant", "Study", "EEGFormat", "EEGParadigm", "User", "OriginalImportFile", "File",
        "Dataset", "Session", "FileStatus", "EegAnalysis", "UserGroup", "AnalysisFlow"
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
        "Participant", "Study", "EEGFormat", "EEGParadigm", "User", "OriginalImportFile", "File",
        "Dataset", "Session", "FileStatus", "EegAnalysis", "UserGroup", "AnalysisFlow"
    ]

    for collection in required_collections:
        if collection not in existing_collections:
            await db.create_collection(collection)
            console.print(f"[yellow]Created missing collection: {collection}[/yellow]")
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

async def load_analysis_flows():
    db = await get_database()
    startup_record = await db.startup.find_one({"_id": 1})
    if startup_record and 'af_config_path' in startup_record:
        file_path = startup_record['af_config_path']
        try:
            with open(file_path, "r") as stream:
                return yaml.safe_load(stream)
        except FileNotFoundError:
            console.print(f"Analysis flows file {file_path} not found.")
        except yaml.YAMLError as exc:
            console.print(f"Error parsing analysis flows YAML: {exc}")
    return None

async def load_config_from_yaml():
    """
    Load configuration from YAML and update the database accordingly.
    Returns:
        bool: True if successful, False otherwise.
    """
    global config
    config = await load_config()
    if config is None:
        return False

    db = await get_database()
    config_collection = db.config

    # Update or insert each section of the configuration
    for section, content in config.items():
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
    return True

async def load_flows_from_yaml():
    """
    Load analysis flows from YAML and update the database accordingly.
    Returns:
        bool: True if successful, False otherwise.
    """
    analysis_flows = await load_analysis_flows()
    if analysis_flows is None:
        return False
    
    db = await get_database()
    analysis_flows_collection = db.AnalysisFlow
        # Update or insert each section of the configuration
    for section, content in analysis_flows.items():
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
            await analysis_flows_collection.update_one(
                {"_id": section},
                {"$set": content},
                upsert=True
            )
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

def create_file_hash(file_path):
    """
    Creates a BLAKE2 hash for a given file.

    Args:
        file_path (str): The path to the file to hash.

    Returns:
        str: The hexadecimal representation of the hash.
    """
    hash_blake2 = hashlib.blake2b()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_blake2.update(chunk)
    return hash_blake2.hexdigest()


def add_status_code(code):
    """
    Maps a status code to a status string.

    Args:
        code (int): The status code to map.

    Returns:
        str: The corresponding status string.
    """
    if code == 200:
        return "NEW"
    elif code == 201:
        return "IMPORTED"
    elif code == 204:
        return "DELETED"
    elif code == 500:
        return "LOAD_ERROR"
    else:
        return "UNHANDLED"

async def generate_database_summary():
    """
    Generates a summary of the database collections and records.

    Returns:
        dict: A dictionary containing the collection names and record counts.
    """
    db = await get_database()
    console = Console()
    table = Table(title="Database Summary (DB Utilities)")
    table.add_column("Collection", style="cyan", no_wrap=True)
    table.add_column("Records", style="green", justify="right")

    json_summary = {}

    collections = await db.list_collection_names()
    for collection_name in collections:
        record_count = await db[collection_name].count_documents({})
        table.add_row(collection_name, str(record_count))
        json_summary[collection_name] = record_count

    console.print(table)
    return json_summary

async def is_config_table_present():
    """
    Check if the configuration collection exists in the database.

    Returns:
        bool: True if the configuration collection exists, False otherwise.
    """
    try:
        db = await get_database()
        collections = await db.list_collection_names()
        return 'config' in collections
    except Exception as e:
        console.print(f"Error checking for config collection: {e}")
        return False
    
async def get_eeg_formats():
    db = await get_database()
    eeg_formats = await db.EEGFormat.find().to_list(length=None)
    return eeg_formats

async def get_eeg_paradigms():
    db = await get_database()
    eeg_paradigms = await db.EEGParadigm.find().to_list(length=None)
    return eeg_paradigms

async def get_analysis_flows():
    db = await get_database()
    analysis_flows = await db.AnalysisFlow.find().to_list(length=None)
    return analysis_flows

async def get_emails():
    db = await get_database()
    users = await db.users.find().to_list(length=None)
    return [
        {
            "id": str(user["_id"]),
            "name": user.get("email")
        }
        for user in users
    ]
    
async def get_participants():
    db = await get_database()
    participants = await db.Participant.find().to_list(length=None)
    return [
        {
            "participant_id": participant["participant_id"],
            "species": participant.get("species"),
            "age": participant.get("age"),
            "age_group": participant.get("age_group"),
            "gender": participant.get("gender"),
            "handedness": participant.get("handedness"),
            "diagnosis": participant.get("diagnosis"),
            "iq_score": participant.get("iq_score"),
            "anxiety_level": participant.get("anxiety_level")
        }
        for participant in participants
    ]
    
async def assign_participant_to_file(participantId, fileId):
    db = await get_database()
    
    # Get the participant
    selected_participant = await db.Participant.find_one({"participant_id": participantId})
    if not selected_participant:
        return {"error": "Participant not found"}
    
    # Check if the file exists
    file = await db.OriginalImportFile.find_one({"upload_id": fileId})
    if not file:
        return {"error": "File not found"}
    
    # Update the file with the participant reference
    result = await db.OriginalImportFile.update_one(
        {"upload_id": fileId},
        {
            "$set": {
                "participant": selected_participant["_id"],
                "status": add_status_code(201)
            }
        }
    )
    
    if result.modified_count == 0:
        return {"error": "File not updated. It may already have this participant."}
    
    return {"success": "Participant assigned to file"}

async def assign_eeg_format_to_file(eeg_format_name, file_id):
    db = await get_database()
    
    # Get the EEGFormat
    selected_eeg_format = await db.EEGFormat.find_one({"name": eeg_format_name})
    if not selected_eeg_format:
        return {"error": "EEGFormat not found"}
    
    # Check if the file exists
    file = await db.OriginalImportFile.find_one({"upload_id": file_id})
    if not file:
        return {"error": "File not found"}
    
    # Update the file with the EEGFormat reference
    result = await db.OriginalImportFile.update_one(
        {"upload_id": file_id},
        {
            "$set": {
                "eeg_format": selected_eeg_format["_id"],
                "status": add_status_code(201)
            }
        }
    )
    
    if result.modified_count == 0:
        return {"error": "File not updated. It may already have this EEGFormat."}
    
    return {"success": "EEGFormat assigned to file"}

async def assign_eeg_paradigm_to_file(eeg_paradigm_name, file_id):
    db = await get_database()
    
    # Get the EEGParadigm
    selected_eeg_paradigm = await db.EEGParadigm.find_one({"name": eeg_paradigm_name})
    if not selected_eeg_paradigm:
        return {"error": "EEGParadigm not found"}
    
    # Check if the file exists
    file = await db.OriginalImportFile.find_one({"upload_id": file_id})
    if not file:
        return {"error": "File not found"}
    
    # Update the file with the EEGParadigm reference
    result = await db.OriginalImportFile.update_one(
        {"upload_id": file_id},
        {
            "$set": {
                "eeg_paradigm": selected_eeg_paradigm["_id"],
                "status": add_status_code(201)
            }
        }
    )
    
    if result.modified_count == 0:
        return {"error": "File not updated. It may already have this EEGParadigm."}
    
    return {"success": "EEGParadigm assigned to file"}

async def assign_tags_to_file(tags, file_id):
    db = await get_database()

    file = await db.OriginalImportFile.find_one({"upload_id": file_id})
    if not file:
        return {"error": "File not found"}
    
    result = await db.OriginalImportFile.update_one(
        {"upload_id": file_id},
        {
            "$addToSet": {
                "tags": {"$each": tags}
            },
            "$set": {
                "status": add_status_code(201)
            }
        }
    )

    if result.modified_count == 0:
        return {"error": "File not updated. It may already have these tags."}
    
    return {"success": "Tags assigned to file"}

async def get_tags(fileId):
    db = await get_database()
    file = await db.OriginalImportFile.find_one({"upload_id": fileId})
    if not file:
        return {"error": "File not found"}
    
    return file.get("tags", [])

async def get_file_runs(original_file_id):
    db = await get_database()
    file_runs = await db.FileRun.find({"original_file_id": ObjectId(original_file_id)}).to_list(length=None)
    if not file_runs:
        return []
    for file_run in file_runs:
        file_run['_id'] = str(file_run['_id'])  # Convert ObjectId to string
        file_run['original_file_id'] = str(file_run['original_file_id'])  # Convert ObjectId to string
        file_run['analysis_run_id'] = str(file_run['analysis_run_id'])  # Convert ObjectId to string
        file_run['run_created_at'] = file_run['run_created_at'].strftime('%H:%M:%S %Y-%m-%d')
        try:
            file_run['run_completed_at'] = file_run['run_completed_at'].strftime('%H:%M:%S %Y-%m-%d')
        except:
            file_run['run_completed_at'] = 'N/A'
    return file_runs

async def get_file_run(file_run_id):
    db = await get_database()
    file_run = await db.FileRun.find_one({"_id": ObjectId(file_run_id)})
    if not file_run:
        return []
    file_run['_id'] = str(file_run['_id'])  # Convert ObjectId to string
    file_run['original_file_id'] = str(file_run['original_file_id'])  # Convert ObjectId to string
    file_run['analysis_run_id'] = str(file_run['analysis_run_id'])  # Convert ObjectId to string
    file_run['run_created_at'] = file_run['run_created_at'].strftime('%H:%M:%S %Y-%m-%d')
    try:
        file_run['run_completed_at'] = file_run['run_completed_at'].strftime('%H:%M:%S %Y-%m-%d')
    except:
        file_run['run_completed_at'] = 'N/A'
    return file_run


async def get_participant(participant_object_id):
    db = await get_database()
    participant_object_id_true = ObjectId(participant_object_id)
    participant = await db.Participant.find_one({"_id": participant_object_id_true})
    if participant:
        return {
            "participant_id": participant["participant_id"],
            "species": participant.get("species"),
            "age": participant.get("age"),
            "age_group": participant.get("age_group"),
            "gender": participant.get("gender"),
            "handedness": participant.get("handedness"),
            "diagnosis": participant.get("diagnosis"),
            "iq_score": participant.get("iq_score"),
            "anxiety_level": participant.get("anxiety_level")
        }

async def get_analysis_from_deployment_id(DeploymentID):
    db = await get_database()
    analysis = await db.EegAnalysis.find_one({"deployment_id": DeploymentID})
    if analysis:
        return {
            "id": str(analysis["_id"]),
            "name": analysis["name"],
            "analysis_flow": analysis.get("analysis_flow"),
            "description": analysis.get("description"),
            "category": analysis.get("category"),
            "valid_formats": analysis.get("valid_formats"),
            "valid_paradigms": analysis.get("valid_paradigms"),
            "valid_files": analysis.get("valid_files"),
            "deployment_id": analysis.get("deployment_id"),
            "output_path": analysis.get("output_path"),
            "parameters": analysis.get("parameters")
        }

async def get_analysisFlow(analysisFlow_object_id):
    db = await get_database()
    analysisFlow_object_id_true = ObjectId(analysisFlow_object_id)
    analysisFlow = await db.AnalysisFlow.find_one({"_id": analysisFlow_object_id_true})
    if analysisFlow:
        return {
            "id": str(analysisFlow["_id"]),
            "name": analysisFlow["name"],
            "description": analysisFlow.get("description"),
            "output_path": analysisFlow.get("output_path"),
            "parameters": analysisFlow.get("parameters")
        }
    
async def get_eeg_format(eeg_format_object_id):
    db = await get_database()
    eeg_format_object_id_true = ObjectId(eeg_format_object_id)
    eeg_format = await db.EEGFormat.find_one({"_id": eeg_format_object_id_true})
    if eeg_format:
        return {
            "id": str(eeg_format["_id"]),
            "name": eeg_format["name"],
            "description": eeg_format.get("description")
        }
    
async def get_eeg_paradigm(eeg_paradigm_object_id):
    db = await get_database()
    eeg_paradigm_object_id_true = ObjectId(eeg_paradigm_object_id)
    eeg_paradigm = await db.EEGParadigm.find_one({"_id": eeg_paradigm_object_id_true})
    if eeg_paradigm:
        return {
            "id": str(eeg_paradigm["_id"]),
            "name": eeg_paradigm["name"],
            "description": eeg_paradigm.get("description")
        }
        
async def add_participant(participant: models.Participant):
    db = await get_database()
    # Convert the Pydantic model to a dictionary
    participant_dict = participant.model_dump()
    result = await db.Participant.insert_one(participant_dict)
    return {
        "id": str(result.inserted_id),
        "participant_id": participant_dict["participant_id"]
    }

async def add_analysis(analysis: models.EegAnalysis):
    db = await get_database()
    # Convert the Pydantic model to a dictionary
    analysis_dict = analysis.model_dump()
    analysis_dict["analysis_flow"] = ObjectId(analysis_dict["analysis_flow"])
    analysis_dict["valid_formats"] = [ObjectId(format_id) for format_id in analysis_dict["valid_formats"]]
    analysis_dict["valid_paradigms"] = [ObjectId(paradigm_id) for paradigm_id in analysis_dict["valid_paradigms"]]
    analysis_dict["valid_files"] = [ObjectId(orginal_file_id) for orginal_file_id in analysis_dict["valid_files"]]

    flow = await db.AnalysisFlow.find_one({"_id": ObjectId(analysis_dict["analysis_flow"])})

    result = await db.EegAnalysis.insert_one(analysis_dict)

    return {
        "id": str(result.inserted_id),
        "analysis_name": analysis_dict["name"],
        "analysis_flow": flow["name"]
    }

async def get_analyses():
    db = await get_database()
    analyses = await db.EegAnalysis.find().to_list(length=None)
    for analysis in analyses:
        analysis['_id'] = str(analysis['_id'])  # Convert ObjectId to string
        analysis['analysis_flow'] = (await db.AnalysisFlow.find_one({"_id": analysis['analysis_flow']}))['name']
        format_names = await db.EEGFormat.find({"_id": {"$in": analysis.get("valid_formats", [])}}).distinct("name")
        paradigm_names = await db.EEGParadigm.find({"_id": {"$in": analysis.get("valid_paradigms", [])}}).distinct("name")
        file_names = await db.OriginalImportFile.find({"_id": {"$in": analysis.get("valid_files", [])}}).distinct("original_name")
        analysis["valid_formats"] = format_names
        analysis["valid_paradigms"] = paradigm_names
        analysis["valid_files"] = file_names
    return analyses
    
            
    
async def get_OriginalImportFile():
    db = await get_database()
    file_catalog = await db.OriginalImportFile.find().to_list(length=None)
    return [
        {
            "upload_id": upload_record["upload_id"],
            "secondary_upload_id": upload_record.get("secondary_upload_id"),
            "original_name": upload_record["original_name"],
            "eeg_format": upload_record.get("eeg_format"),
            "is_primary_file": upload_record.get("is_primary_file"),
            "has_secondary_file": upload_record.get("has_secondary_file"),
            "secondary_filename": upload_record.get("secondary_filename"),
            "dataset_id": upload_record.get("dataset_id"),
            "dataset_name": upload_record.get("dataset_name"),
            "dataset_description": upload_record.get("dataset_description"),
            "eeg_paradigm": upload_record.get("eeg_paradigm"),
            "status": upload_record.get("status"),
            "date_added": upload_record.get("date_added"),
            "hash": upload_record.get("hash"),
            "tags": upload_record.get("tags"),
            "size": upload_record.get("size"),
            "remove_upload": upload_record.get("remove_upload"),
            "upload_email": upload_record.get("upload_email"),
            "participant": upload_record.get("participant"),
        }
        for upload_record in file_catalog
    ]
    
async def get_OriginalImportFile_by_id(upload_id):
    db = await get_database()
    file_record = await db.OriginalImportFile.find_one({"upload_id": upload_id})
    if file_record:
        return file_record
    else:
        return {"error": "File not found"}


async def get_matchingFiles(valid_formats, valid_paradigms):
    db = await get_database()
    valid_formats = [ObjectId(format_id) for format_id in valid_formats]
    valid_paradigms = [ObjectId(paradigm_id) for paradigm_id in valid_paradigms]
    
    valid_files = await db.OriginalImportFile.find({
        "eeg_format": {"$in": valid_formats},
        "eeg_paradigm": {"$in": valid_paradigms}
    }).to_list(length=None)
    
    return valid_files

async def get_form_options(FormField: str):
    db = await get_database()
    options = await db.FormInfo.find_one({"name": FormField})
    if options:
        return {
            "name": options["name"],
            "description": options.get("description"),
            "form_options": options.get("form_options")
        }

async def get_import_catalog():
    db = await get_database()
    import_catalog = await db.import_catalog.find().to_list(length=None)
    return [
        {
            "upload_id": import_record["upload_id"],
            "original_name": import_record["original_name"],
            "is_primary_file": import_record.get("is_primary_file"),
            "has_secondary_file": import_record.get("has_secondary_file"),
            "secondary_filename": import_record.get("secondary_filename"),
            "secondary_upload_id": import_record.get("secondary_upload_id"),
            "dataset_id": import_record.get("dataset_id"),
            "dataset_name": import_record.get("dataset_name"),
            "dataset_description": import_record.get("dataset_description"),
            "eeg_format": import_record.get("eeg_format"),
            "eeg_paradigm": import_record.get("eeg_paradigm"),
            "status": import_record.get("status"),
            "date_added": import_record.get("date_added"),
            "remove_import": import_record.get("remove_import"),
            "hash": import_record.get("hash"),
            "sample_rate": import_record.get("sample_rate"),
            "n_channels": import_record.get("n_channels"),
            "n_epochs": import_record.get("n_epochs"),
            "total_samples": import_record.get("total_samples"),
            "mne_load_error": import_record.get("mne_load_error"),
            "upload_email": import_record.get("upload_email")
        }
        for import_record in import_catalog
    ]

async def get_dataset_catalog():
    db = await get_database()
    dataset_catalog = await db.dataset_catalog.find().to_list(length=None)
    return [
        {
            "dataset_name": dataset["dataset_name"],
            "dataset_id": dataset["dataset_id"],
            "description": dataset.get("description")
        }
        for dataset in dataset_catalog
    ]
    
async def get_dataset_stats():
    db = await get_database()
    dataset_catalog = await db.dataset_catalog.find().to_list(length=None)
    
    # Count number of import_catalog records associated with each dataset_id
    import_counts = await db.import_catalog.aggregate([
        {"$group": {"_id": "$dataset_id", "file_count": {"$sum": 1}}}
    ]).to_list(length=None)
    
    # Convert list of dicts into a dict for quick lookup
    count_dict = {item["_id"]: item["file_count"] for item in import_counts}
    
    return [
        {
            "dataset_name": dataset["dataset_name"],
            "dataset_id": dataset["dataset_id"],
            "description": dataset.get("description"),
            "file_count": count_dict.get(dataset["dataset_id"], 0)
        }
        for dataset in dataset_catalog
    ]

async def add_dataset(dataset_catalog_entry):
    print(f"📊 Adding dataset: {dataset_catalog_entry}")
    db = await get_database()
    existing_dataset = await db.dataset_catalog.find_one({"dataset_id": dataset_catalog_entry["dataset_id"]})
    if not existing_dataset:
        result = await db.dataset_catalog.insert_one(dataset_catalog_entry)
        return {
            "id": str(result.inserted_id),
            "name": dataset_catalog_entry["dataset_name"],
            "description": dataset_catalog_entry.get("description")
        }
    else:
        return {
            "id": str(existing_dataset["_id"]),
            "name": existing_dataset["dataset_name"],
            "description": existing_dataset.get("description")
        }

async def update_dataset(dataset_catalog_entry):
    db = await get_database()
    result = await db.dataset_catalog.update_one(
        {"dataset_id": dataset_catalog_entry["dataset_id"]},
        {"$set": {
            "dataset_name": dataset_catalog_entry["dataset_name"],
            "description": dataset_catalog_entry.get("description")
        }}
    )
    if result.modified_count == 1:
        return await db.dataset_catalog.find_one({"dataset_id": dataset_catalog_entry["dataset_id"]})
    else:
        return {"error": "Dataset not found"}



async def add_dataset_catalog(dataset_catalog_entry):
    print(f"📊 Adding dataset: {dataset_catalog_entry}")
    db = await get_database()
    try:
        await db.Dataset.update_one(
            {"dataset_id": dataset_catalog_entry['dataset_id']},
            {"$set": dataset_catalog_entry},
            upsert=True
        )
        logging.info(f"Dataset added to database with ID: {dataset_catalog_entry['dataset_id']}")
    except Exception as e:
        logging.error(f"Error adding dataset: {str(e)}")
        raise e
    return dataset_catalog_entry

async def add_original_import_file_catalog(original_import_file_catalog_entry):
    print(f"📁 Adding OriginalImportFile: {original_import_file_catalog_entry}")
    db = await get_database()
    try:
        await db.OriginalImportFile.update_one(
            {"upload_id": original_import_file_catalog_entry['upload_id']},
            {"$set": original_import_file_catalog_entry},
            upsert=True
        )
        logging.info(f"Metadata added to database for file: {original_import_file_catalog_entry['original_name']}")
    except Exception as e:
        logging.error(f"Error adding upload: {str(e)}")
        raise e
    return original_import_file_catalog_entry

async def align_secondary_files():
    db = await get_database()
    async for row in db.OriginalImportFile.find():
        if row['original_name'].endswith(".set"):
            update_data = {"is_primary_file": True}
            secondary_filename = row['original_name'].replace(".set", ".fdt")
            secondary_file = await db.OriginalImportFile.find_one({"original_name": {"$regex": f"^{secondary_filename}$", "$options": "i"}})
            if secondary_file:
                update_data.update({
                    "has_secondary_file": True,
                    "secondary_filename": secondary_filename,
                    "secondary_upload_id": secondary_file['upload_id']
                })
            else:
                update_data.update({
                    "has_secondary_file": False,
                    "secondary_filename": secondary_filename,
                    "secondary_upload_id": None
                })
        else:
            update_data = {"is_primary_file": False}

        await db.OriginalImportFile.update_one({"_id": row['_id']}, {"$set": update_data})
            
async def delete_uploads_and_save_info_files():
    FOLDER_PATHS = await get_folder_paths()
    UPLOAD_PATH = FOLDER_PATHS["uploads"]
    INFO_PATH = FOLDER_PATHS["info_archive"]
    db = await get_database()
    async for row in db.OriginalImportFile.find({"remove_upload": True}):
        os.remove(os.path.join(UPLOAD_PATH, row['original_name']))
        move(
            os.path.join(UPLOAD_PATH, row['upload_id'] + ".info"),
            os.path.join(INFO_PATH, row['upload_id'] + ".info"),
        )

async def ingest_info_files(info_files):
    async def extract_metadata(file_metadata):
        db = await get_database()
        folder_path = await get_folder_paths()
        folder_path = folder_path["uploads"]
        participant = await db.Participant.find_one({"participant_id": "Empty"})
        paradigm = await db.EEGParadigm.find_one({"name": "Unassigned"})
        EEGFormat = await db.EEGFormat.find_one({"name": "Unassigned"})
        original_import_file_catalog_entry = {
            "upload_id": file_metadata.get("ID", "NA"),
            "original_name": file_metadata["MetaData"].get("filename", "NA"),
            "dataset_id": file_metadata["MetaData"].get("datasetId", "NA"),
            # "upload_user": file_metadata["MetaData"].get("user", "NA"), TODO: Add user support
            "status": add_status_code(200),
            "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hash": create_file_hash(
                os.path.join(
                    folder_path,
                    os.path.basename(file_metadata["Storage"].get("Path", "")),
                )
            ),
            "remove_upload": False,
            "participant": participant["_id"],
            "eeg_format": EEGFormat["_id"],
            "eeg_paradigm": paradigm["_id"],
        }
            
        dataset_catalog_entry = {
            "dataset_id": file_metadata["MetaData"].get("datasetId", "NA"),
            "dataset_name": file_metadata["MetaData"].get("datasetName", "NA"),
            "description": "",
        }
        return original_import_file_catalog_entry, dataset_catalog_entry
    for info_file in info_files:
        with open(info_file, "r") as f:
            file_metadata = json.load(f)
        id = file_metadata.get("ID")
        file = await db.OriginalImportFile.find_one({"upload_id": id})
        if not file:
            original_import_file_catalog_entry, dataset_catalog_entry = await extract_metadata(file_metadata)
            dataset_result = await add_dataset_catalog(dataset_catalog_entry)
            upload_result = await add_original_import_file_catalog(original_import_file_catalog_entry)
            print(f"Added dataset with ID: {dataset_result['dataset_id']}")
            print(f"Added upload with ID: {upload_result['upload_id']}")

async def process_new_uploads(upload_dir):
    async def update_file_catalog(info_files):
        await ingest_info_files(info_files)
        await align_secondary_files()
        await delete_uploads_and_save_info_files()

    def find_info_files(upload_dir):
        info_files = glob.glob(os.path.join(upload_dir, "*.info"))
        logging.info(f"Detected {len(info_files)} .info files in {upload_dir}.")
        return info_files

    logging.info(f"Scanning upload directory: {upload_dir}")
    info_files = find_info_files(upload_dir)
    await update_file_catalog(info_files)
    logging.info("Upload and import catalogs updated.")
    
async def get_upload_paths(upload_id):
    db = await get_database()
    FOLDER_PATHS = await get_folder_paths()
    UPLOAD_PATH = FOLDER_PATHS["uploads"]
    TEMP_PATH = FOLDER_PATHS["temp"]
    file_record = await db.OriginalImportFile.find_one({"upload_id": upload_id})
    if not file_record:
        raise ValueError(f"Upload ID {upload_id} not found in the database.")
    primary_upload_path = os.path.join(UPLOAD_PATH, upload_id)
    secondary_upload_path = os.path.join(UPLOAD_PATH, file_record['secondary_upload_id']) if file_record.get('secondary_upload_id') else None
    primary_import_path = os.path.join(TEMP_PATH, file_record['original_name'])
    secondary_import_path = os.path.join(TEMP_PATH, file_record['secondary_filename']) if file_record.get('secondary_filename') else None
    return {
        "upload_id": upload_id,
        "primary_upload_path": primary_upload_path,
        "secondary_upload_path": secondary_upload_path,
        "primary_import_path": primary_import_path,
        "secondary_import_path": secondary_import_path
    }
    
async def clean_import_files(upload_id):
    import_file_paths = await get_upload_paths(upload_id)
    primary_dest_path = import_file_paths['primary_import_path']
    secondary_dest_path = import_file_paths['secondary_import_path']

    if os.path.exists(primary_dest_path):
        os.remove(primary_dest_path)
        print(f"Removed SET file {primary_dest_path}")
    if secondary_dest_path and os.path.exists(secondary_dest_path):
        os.remove(secondary_dest_path)
        print(f"Removed secondary file {secondary_dest_path}")

async def copy_import_files(upload_id):
    # Copy the SET and secondary files to the import path
    import_file_paths = await get_upload_paths(upload_id)
    primary_dest_path = import_file_paths['primary_import_path']
    secondary_dest_path = import_file_paths['secondary_import_path']
    primary_src_path = import_file_paths['primary_upload_path']
    secondary_src_path = import_file_paths['secondary_upload_path']

    if primary_src_path:
        copy(primary_src_path, primary_dest_path)
        print(f"Copied SET file {primary_src_path} to {primary_dest_path}")
    
    if secondary_src_path:
        copy(secondary_src_path, secondary_dest_path)
        print(f"Copied secondary file {secondary_src_path} to {secondary_dest_path}")
    return primary_dest_path, secondary_dest_path

def get_core_eeg_info( primary_file_path ):
    """
    Extracts metadata from an EEG file.

    Args:
        primary_file_path (str): The path to the EEG file.

    Returns:
        dict: A dictionary containing the metadata of the EEG file.
    """

    try:
        # Load the EEG data using MNE
        try:
            EEG = mne.io.read_raw_eeglab(primary_file_path, preload=True)
            info = EEG.info
            eeg_core_info = {
                'mne_load_error': False,  # This key can be used to track the error in the database
                'mne_data_type': 'raw_eeglab',
                'n_channels': len(info['ch_names']),
                'sample_rate': info['sfreq'],
                'n_epochs': 1,
                'total_samples': len(EEG)
            }
        except Exception as e:
            print(f"Error loading as raw_eeglab: {e}")
            EEG = mne.io.read_epochs_eeglab(primary_file_path)
            info = EEG.info
            eeg_core_info = {
                'mne_load_error': False,  # This key can be used to track the error in the database
                'mne_data_type': 'epochs_eeglab',
                'n_channels': len(info['ch_names']),
                'sample_rate': info['sfreq'],
                'n_epochs': len(EEG) if hasattr(EEG, '__len__') else 1,
                'total_samples': (len(EEG) if hasattr(EEG, '__len__') else 1) * len(EEG.times)
            }
    except Exception as e:
        print(f"Error loading EEG file: {e}")
        # Handle potential errors from the entire block
        eeg_core_info = {
            'mne_load_error': True,  # This key can be used to track the error in the database
            'mne_data_type': 'error',  # This key can be used to track the error in the database
            'n_channels': 0,
            'sample_rate': 0,
            'n_epochs': 0,
            'total_samples': 0
        }
        # Optionally log the error or handle it as needed

    return eeg_core_info


async def get_EEG_Data(upload_id):
    try: 
        primary_dest_path, secondary_dest_path = await copy_import_files(upload_id)
        
        if secondary_dest_path is not None:
            try:
                if primary_dest_path.endswith(".set"):
                    # Read EEGLAB file info 
                    eeg_data = await asyncio.to_thread(mne.io.read_raw_eeglab, primary_dest_path, preload=True, verbose=True)

                    psd = eeg_data.compute_psd(fmin=1, fmax=80)
        
                    fig = psd.plot(show=False)
                    
                    tempPath = await get_folder_paths()
                    tempPath = tempPath["temp"]
                    psdPath = f"{tempPath}/psd_{upload_id}.png"
                    fig.savefig(psdPath)
                elif not primary_dest_path.endswith(".fdt"):
                    eeg_data = await asyncio.to_thread(mne.io.read_raw, primary_dest_path, preload=True, verbose=True)
                else:
                    eeg_data = None
            
            except Exception as e:
                logging.error(f"Error reading EEG data: {str(e)}")
                raise
            
            if os.path.exists(primary_dest_path):
                await asyncio.to_thread(os.remove, primary_dest_path)
                logging.info(f"Removed SET file {primary_dest_path}")
            if secondary_dest_path and os.path.exists(secondary_dest_path):
                await asyncio.to_thread(os.remove, secondary_dest_path)
                logging.info(f"Removed FDT file {secondary_dest_path}")
            
            return eeg_data, psdPath
    except Exception as e:
        logging.error(f"Error getting EEG data: {str(e)}")
        raise
