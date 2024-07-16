# Standard library imports
from datetime import datetime
import json
import os
import asyncio
import time

# Third-party library imports
import mne
from prefect import task, flow

# Project-specific imports
import db as flow_db
# from signalfloweeg.portal.db_connection import get_database
# from signalfloweeg.portal.import_catalog import copy_import_files
# from signalfloweeg.portal.portal_utils import load_config
# from signalfloweeg.viz.heatmap import heatmap_power
from motor.motor_asyncio import AsyncIOMotorDatabase


# ────────────────────────────────────────────────────────────────────────────────
# Task Definitions
# ────────────────────────────────────────────────────────────────────────────────

@task(retries=1)
async def loadconfig():
    # Load configuration file
    config = await flow_db.load_config()
    return config

@task()
async def get_file_and_analyses(db: AsyncIOMotorDatabase):
    loop = asyncio.get_event_loop()
    file = await loop.run_in_executor(None, db.import_catalog.find_one)
    analyses = await loop.run_in_executor(None, db.eeg_analyses.find().to_list, None)
    results = [file._result, analyses._result]
    return results

@task
async def getRaw(upload_id: str, upload_path: str):
    """
    This function is used to get the raw EEG data from the specified upload path. 

    Parameters:
    upload_id (str): The ID of the upload.
    upload_path (str): The path where the upload is located.

    Returns:
    raw_eeg: The raw EEG data.
    """

    try: 
        set_dest_path, fdt_dest_path = await flow_db.copy_import_files(upload_id)
        
        # Use asyncio.to_thread for CPU-bound operations
        raw_eeg = await asyncio.to_thread(mne.io.read_raw_eeglab, set_dest_path, preload=True, verbose=False)
                                                                                                
        if os.path.exists(set_dest_path):
            await asyncio.to_thread(os.remove, set_dest_path)
            print(f"Removed SET file {set_dest_path}")
        if fdt_dest_path and os.path.exists(fdt_dest_path):
            await asyncio.to_thread(os.remove, fdt_dest_path)
            print(f"Removed FDT file {fdt_dest_path}")
        return raw_eeg
    
    except Exception as e:
        print("Exception Occurred when creating Raw Obj: " + str(e))
        raise


@task(name="FakeAnalysis", description="Run a fake analysis on the file.")
async def fakeAnalysis(importID: str, output_path: str):
    """
    This function is used to run a fake analysis on the file and save the result in the specified output path.

    Parameters:
    importID (str): The ID of the import.
    output_path (str): The path where the result of the analysis will be saved.
    """

    analysisName = "Fake Analysis"
    savePath = os.path.join(output_path, (analysisName + "_" + importID))
    print(f"Running analysis on file {importID}")

    with open(savePath, 'a') as file:
        file.write(f"Ran {analysisName} on {importID}\n")

@task(name="CreateMetaData", description="Save metadata of the file and what analyses were run on it to a .info file.")
async def saveMetaData(fileImport: dict, output_path: str, analysisList: list):
    """
    This function is used to save the metadata of the file and the analyses that were run on it to a .info file.

    Parameters:
    fileImport (dict): The import catalog entry of the file.
    output_path (str): The path where the .info file will be saved.
    analysisList (list): The list of analyses that were run on the file.
    """

    savePath = os.path.join(output_path, (fileImport['upload_id'] + ".info"))

    metadata = {
        'ID': fileImport['upload_id'],
        'analyses_attempted': analysisList,
        'eeg_format': fileImport['eeg_format'],
        'eeg_paradigm': fileImport['eeg_paradigm'],
        'execution_date': datetime.now().isoformat()
    }

    with open(savePath, 'a') as file:
        file.write(json.dumps(metadata, indent=4) + "\n")

# ────────────────────────────────────────────────────────────────────────────────
# Analysis Flow
# ────────────────────────────────────────────────────────────────────────────────


@flow(log_prints=True)
async def AnalysisFlow(filename: str):
    """
    This is a Prefect 2 flow that schedules all relevant analyses for a given file. 

    The function first loads a configuration file and extracts the paths for upload and output directories.
    It then establishes a connection with the database and retrieves the first file from the ImportCatalog collection 
    and all records from the EegAnalyses collection. For each analysis in the EegAnalyses collection, it checks if the 
    file's EEG format and paradigm match the valid formats and paradigms for the analysis. If a match is found, 
    it retrieves the raw EEG data for the file and runs the corresponding analysis functions. If the analysis 
    function is successful, the name of the analysis is added to a list. If any analyses were run, it saves 
    metadata for the file. 
    """
    
    config = await loadconfig()  # Load configuration file
    upload_path = config["folder_paths"]["uploads"]  # Get upload directory path
    output_path = config["folder_paths"]["output"]  # Get output directory path
# 1000_6_to_1100_9_aaebci_NS_09-05-2023_20230905_121427.set
    db = await flow_db.get_database()
    test_file = await db.OriginalImportFile.find_one({"upload_id": "d737c2416b20da38c42853012e431279"})
    upload_id = test_file["upload_id"]
    tasks = []

    raw_eeg = await getRaw(upload_id, upload_path)
    tasks.append(fakeAnalysis(upload_id, output_path, wait_for=[raw_eeg]))

    if tasks:
        await asyncio.gather(*tasks)  # Run all analysis tasks in parallel

    # await saveMetaData(file, output_path, ["FakeAnalysis"])  # Save metadata for the file if any analyses were run

    return "Success"


if __name__ == "__main__":
    AnalysisFlow()
