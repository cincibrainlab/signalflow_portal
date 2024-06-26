# Standard library imports
from datetime import datetime
import json
import os
import asyncio

# Third-party library imports
import mne
import sqlalchemy as sa
from prefect import task, flow

# Project-specific imports
from signalfloweeg.portal.db_connection import get_session
from signalfloweeg.portal.import_catalog import copy_import_files
from signalfloweeg.portal.portal_utils import load_config
from signalfloweeg.viz.heatmap import heatmap_power
from signalfloweeg.portal.models import ImportCatalog, EegAnalyses



# ────────────────────────────────────────────────────────────────────────────────
# Task Definitions
# ────────────────────────────────────────────────────────────────────────────────

@task (retries = 1)
def getRaw(upload_id: str, upload_path: str):
    """
    This function is used to get the raw EEG data from the specified upload path. 

    Parameters:
    upload_id (str): The ID of the upload.
    upload_path (str): The path where the upload is located.

    Returns:
    raw_eeg: The raw EEG data.
    """

    try: 
        set_dest_path, fdt_dest_path = copy_import_files(upload_id)
        raw_eeg = mne.io.read_raw(set_dest_path, preload=True, verbose=False)

        if os.path.exists(set_dest_path):
            os.remove(set_dest_path)
            print(f"Removed SET file {set_dest_path}")
        if fdt_dest_path and os.path.exists(fdt_dest_path):
            os.remove(fdt_dest_path)
            print(f"Removed FDT file {fdt_dest_path}")
        return raw_eeg
    
    except Exception as e:
        print("Exception Occured when creating Raw Obj: " + str(e))
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
def fakeAnalysis(importID: str, output_path: str):
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
def saveMetaData(fileImport: ImportCatalog, output_path: str, analysisList: list):
    """
    This function is used to save the metadata of the file and the analyses that were run on it to a .info file.

    Parameters:
    fileImport (ImportCatalog): The import catalog of the file.
    output_path (str): The path where the .info file will be saved.
    analysisList (list): The list of analyses that were run on the file.
    """

    savePath = os.path.join(output_path, (fileImport.upload_id + ".info"))

    metadata = {
        'ID': fileImport.upload_id,
        'analyses_attempted': analysisList,
        'eeg_format': fileImport.eeg_format,
        'eeg_paradigm': fileImport.eeg_paradigm,
        'execution_date': datetime.now().isoformat()
        }

    with open(savePath, 'a') as file:
        file.write(json.dumps(metadata, indent=4) + "\n")

# ────────────────────────────────────────────────────────────────────────────────
# Analysis Flow
# ────────────────────────────────────────────────────────────────────────────────

ANALYSIS_FUNCTIONS = { # Dictionary of analysis functions
    "heatmap": heatmap,
    "Test1": fakeAnalysis
}


@flow(log_prints=True)
def AnalysisFlow(filename: str):
    """
    This is a Prefect 2 flow that schedules all relevant analyses for a givin file. 

    The function first loads a configuration file and extracts the paths for upload and output directories.
    It then establishes a session with a database and retrieves the first file from the ImportCatalog table 
    and all records from the EegAnalyses table. For each analysis in the EegAnalyses table, it checks if the 
    file's EEG format and paradigm match the valid formats and paradigms for the analysis. If a match is found, 
    it retrieves the raw EEG data for the file and runs the corresponding analysis functions. If the analysis 
    function is successful, the name of the analysis is added to a list. If any analyses were run, it saves 
    metadata for the file. 
    """

    config = load_config()  # Load configuration file
    upload_path = config["folder_paths"]["uploads"]  # Get upload directory path
    output_path = config["folder_paths"]["output"]  # Get output directory path

    with get_session() as session:  # Establish a session with the database
        file = session.query(ImportCatalog).first()  # Get the first file from the ImportCatalog table
        analyses = session.query(EegAnalyses).all()  # Get all records from the EegAnalyses table
        session.close()

    analysis_list = []
    for analysis in analyses:
        print(f"Analysis {analysis.name} has valid formats {analysis.valid_formats} and valid paradigms {analysis.valid_paradigms}")
        if file.eeg_format in analysis.valid_formats and file.eeg_paradigm in analysis.valid_paradigms:
            print(f"Running analysis {analysis.name} on file {file.upload_id}")
            raw_eeg = getRaw(file.upload_id, upload_path)  # Retrieve raw EEG data for the file

            analysis_function = ANALYSIS_FUNCTIONS.get(analysis.name)
            if analysis_function:
                analysis_function(file.upload_id, output_path, wait_for=[raw_eeg])  # Run the corresponding analysis function
                analysis_list.append(analysis.name)  # Add the name of the analysis to a list
            else:
                print(f"No function found for analysis {analysis.name}")
    if len(analysis_list) > 0:
        saveMetaData(file, output_path, analysis_list)  # Save metadata for the file if any analyses were run
    return "Success"


if __name__ == "__main__":
    AnalysisFlow()

