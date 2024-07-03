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
from signalfloweeg.portal.db_connection import get_database
from signalfloweeg.portal.import_catalog import copy_import_files
from signalfloweeg.portal.portal_utils import load_config
from signalfloweeg.viz.heatmap import heatmap_power

# ────────────────────────────────────────────────────────────────────────────────
# Task Definitions
# ────────────────────────────────────────────────────────────────────────────────

@task(retries=1)
async def loadconfig():
    # Load configuration file
    config = await load_config()
    return config

@task(retries=1)
async def get_file_and_analyses():
    db = await get_database()
    file = await db.import_catalog.find_one()  # Get the first file from the ImportCatalog collection
    analyses = await db.eeg_analyses.find().to_list(None)  # Get all records from the EegAnalyses collection
    return file, analyses

@task(retries=1)
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
        set_dest_path, fdt_dest_path = await copy_import_files(upload_id)
        raw_eeg = mne.io.read_raw(set_dest_path, preload=True, verbose=False)

        if os.path.exists(set_dest_path):
            os.remove(set_dest_path)
            print(f"Removed SET file {set_dest_path}")
        if fdt_dest_path and os.path.exists(fdt_dest_path):
            os.remove(fdt_dest_path)
            print(f"Removed FDT file {fdt_dest_path}")
        return raw_eeg
    
    except Exception as e:
        print("Exception Occurred when creating Raw Obj: " + str(e))
        raise

@task
def heatmap(raw: mne.io.Raw):
    """
    This function is used to create a heatmap of the raw EEG data.

    Parameters:
    raw (mne.io.Raw): The raw EEG data.
    """

    epochs = mne.make_fixed_length_epochs(raw, duration=5, preload=False)
    heatmap_power(epochs)

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

ANALYSIS_FUNCTIONS = {  # Dictionary of analysis functions
    "heatmap": heatmap,
    "Test1": fakeAnalysis
}

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

    file, analyses = await get_file_and_analyses()  # Get file and analyses

    analysis_list = []
    tasks = []
    for analysis in analyses:
        if file['eeg_format'] in analysis['valid_formats'] and file['eeg_paradigm'] in analysis['valid_paradigms']:
            raw_eeg = await getRaw(file['upload_id'], upload_path, wait_for=[file])  # Retrieve raw EEG data for the file

            analysis_function = ANALYSIS_FUNCTIONS.get(analysis['name'])
            if analysis_function:
                tasks.append(analysis_function(file['upload_id'], output_path, wait_for=[raw_eeg]))  # Schedule the analysis function
                analysis_list.append(analysis['name'])  # Add the name of the analysis to a list
            else:
                print(f"No function found for analysis {analysis['name']}")

    if tasks:
        await asyncio.gather(*tasks)  # Run all analysis tasks in parallel

    if analysis_list:
        await saveMetaData(file, output_path, analysis_list)  # Save metadata for the file if any analyses were run

    return "Success"


if __name__ == "__main__":
    AnalysisFlow()
