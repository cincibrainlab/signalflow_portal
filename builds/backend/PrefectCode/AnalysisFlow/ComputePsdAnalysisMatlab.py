# Standard library imports
import asyncio
import sys
import os
# Signalflow imports
sys.path.append("builds/backend")
import db as flow_db
sys.path.append("builds/backend/PrefectCode/AnalysisFlow/")
from PrefectCode import UtilityTasks 
# Third-party library imports
from prefect import flow, task
from bson import ObjectId
import matlab.engine
import logging
from datetime import datetime

global output_files
output_files = []

@task(name="update_file_runs", retries=1, description="Update the file runs with the output files.")
async def update_file_runs(analysis_id, importID):
    db = await flow_db.get_database()
    original_file = await db.OriginalImportFile.find_one({"upload_id": importID})
    if not original_file:
        raise ValueError(f"Original file with upload_id {importID} not found")

    file_runs = original_file.get("fileRuns", [])
    if not file_runs:
        raise ValueError(f"No file runs found for upload_id {importID}")

    matching_file_run = await db.FileRun.find_one({
        "_id": {"$in": file_runs},
        "analysis_run_id": ObjectId(analysis_id)
    })

    if not matching_file_run:
        raise ValueError(f"No matching file run found for analysis_id {analysis_id}")

    await db.FileRun.update_one(
        {"_id": matching_file_run["_id"]},
        {"$set": {
            "output_files": output_files,
            "run_completed_at": datetime.now(),
            "status": "completed"
        }}
    )


@flow(name="ComputePsdAnalysisMatlab_Flow", description="Run a Template analysis on the file.")
async def ComputePsdAnalysisMatlab_Flow(importID: str, analysis_flow: str, analysis_id: str):
    config = await UtilityTasks.loadconfig()  # Load configuration file
    upload_path = config["folder_paths"]["uploads"]  # Get upload directory path
    output_files = []


    db = await flow_db.get_database()
    
    # Get data from the database about the analysis
    EEGAnalysis = await db.EegAnalysis.find_one({"_id": ObjectId(analysis_id)})
    output_path = EEGAnalysis["output_path"]
    
    # Get the analysis flow from the database
    AnalysisFlow = await db.AnalysisFlow.find_one({"name": analysis_flow})
    
    # Get the file from the database
    original_file = await db.OriginalImportFile.find_one({"upload_id": importID})
    upload_id = original_file["upload_id"]
    
    # Start the Matlab engine
    eng = matlab.engine.start_matlab()
    eng.addpath(r'builds/backend/PrefectCode/matlab/eeglab/')
    eng.eval("eeglab('nogui')")
    
    # Import the file - Will save as 'EEG' in the Matlab workspace
    primary_dest_path, secondary_dest_path = await UtilityTasks.getRawMatlab(eng, upload_id, upload_path)

    if secondary_dest_path is not None:
    # Perform Preprocessing here
        eng.eval('[spectra, freqs] = spectopo(EEG.data, 0, EEG.srate);', nargout=0)
        eng.eval("fig = figure('visible', 'off');", nargout=0)
        eng.eval('plot(freqs, spectra);', nargout=0)
        eng.eval('title("Power Spectral Density");', nargout=0)
        eng.eval('xlabel("Frequency (Hz)");', nargout=0)
        eng.eval('ylabel("Power/Frequency (dB/Hz)");', nargout=0)
        eng.eval('saveas(fig, "' + output_path + '/' + upload_id +'_psd.png");', nargout=0)
        output_files.append(output_path + '/psd_' + upload_id +'.png')
    

    # This will run all the tasks listed in parallel. Vastly speeds up code execution.
    # This is not recommended for signal processing and analysis functions. 
    # Because the order of the tasks is not guaranteed.
    # This is only recommended for tasks that can be run in parallel.
    # For example, creating multiple figures or saving multiple files.
    await update_file_runs(analysis_id, importID)
    tasks = []
    if tasks:
        await asyncio.gather(*tasks)  # Run all analysis tasks in parallel