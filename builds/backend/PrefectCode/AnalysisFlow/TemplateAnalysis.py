# Standard library imports
import asyncio
from datetime import datetime
import sys
import pandas as pd
# Signalflow imports
sys.path.append("builds/backend")
import db as flow_db
sys.path.append("builds/backend/PrefectCode/AnalysisFlow/")
from PrefectCode import UtilityTasks 
# Third-party library imports
from prefect import flow, task
from autoreject import AutoReject
import mne
from bson import ObjectId

global output_files
output_files = []

@task(name="run_filters", retries=1, description="")
async def run_filters(raw, filters):
    for filter in filters:
        if filter["name"] == "notch":
            raw.notch_filter(freqs=filter["freqs"], filter_length=filter["filter_length"], phase=filter["phase"])
        elif filter["name"] == "highpass":
            raw.filter(l_freq=filter["freqs"], h_freq=None, filter_length=filter["filter_length"], phase=filter["phase"])
        elif filter["name"] == "lowpass":
            raw.filter(l_freq=None, h_freq=filter["freqs"], filter_length=filter["filter_length"], phase=filter["phase"])
        elif filter["name"] == "bandpass":
            raw.filter(l_freq=filter["freqs"][0], h_freq=filter["freqs"][1], filter_length=filter["filter_length"], phase=filter["phase"])
    return raw
            
@task(name="make_epochs", retries=1, description="")
async def make_epochs(raw, duration=1):
    raw = raw.copy().set_eeg_reference(ref_channels='average')
    epochs = mne.make_fixed_length_epochs(raw, duration=duration, preload=True)
    return epochs

@task(name="run_autoreject", retries=1, description="")
async def run_autoreject(epochs):
    
    ar = AutoReject()
    epochs, reject_log = ar.fit_transform(epochs, return_log=True)
    return epochs, reject_log

@task(name="run_ica", retries=1, description="")
async def run_ica(epochs):
    ica = mne.preprocessing.ICA()
    ica.fit(epochs)
    ica.exclude = [1,2,3] # This is bad practice, but just for example
    ica.apply(epochs)
    return epochs

@task(name="get_psd_graph", retries=1, description="")
async def get_psd_graph(epochs, importID, output_path):
    psd = epochs.compute_psd(fmin=1, fmax=80)
        
    fig = psd.plot(show=False)
    
    fig.savefig(f"{output_path}/psd_{importID}.png")
    output_files.append(f"{output_path}/psd_{importID}.png")
    
@task(name="SaveEEG", retries=1, description="Save the EEG data to the output directory.")
async def SaveEEG(raw, importID, output_path):
    raw.save(f"{output_path}/raw_{importID}.fif", overwrite=True)
    output_files.append(f"{output_path}/raw_{importID}.fif")

@task(name="SaveCSV", retries=1, description="Save the EEG data to the output directory.")
async def SaveCSV(raw, importID, output_path):
    df = raw.to_data_frame()
    df.to_csv(f"{output_path}/csv_{importID}.csv")
    output_files.append(f"{output_path}/csv_{importID}.csv")

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

@flow(name="TemplateAnalysis_Flow", description="Run a Template analysis on the file.")
async def TemplateAnalysis_Flow(importID: str, analysis_flow: str, analysis_id: str):
    config = await UtilityTasks.loadconfig()  # Load configuration file
    upload_path = config["folder_paths"]["uploads"]  # Get upload directory path
    output_files = []
    tasks = []

    db = await flow_db.get_database()
    
    # Get data from the database about the analysis
    EEGAnalysis = await db.EegAnalysis.find_one({"_id": ObjectId(analysis_id)})
    output_path = EEGAnalysis["output_path"]
    
    # Get the analysis flow from the database
    # AnalysisFlow = await db.AnalysisFlow.find_one({"name": analysis_flow})
    
    # Get the file from the database
    original_file = await db.OriginalImportFile.find_one({"upload_id": importID})
    upload_id = original_file["upload_id"]
    
    # Import the file
    raw_eeg = await UtilityTasks.getRawPython(upload_id, upload_path)
    
    if raw_eeg is not None:
        raw = raw_eeg
        # Perform Preprocessing here
        
        # Apply filters
        # You can add and remove filters as needed.
        filters = [
            {
                "name" : "notch",
                "freqs": 60,
                "filter_length": "auto",
                "phase": "zero"
            },
            {
                "name" : "notch",
                "freqs": 120,
                "filter_length": "auto",
                "phase": "zero"
            },
            {
                "name" : "notch",
                "freqs": 180,
                "filter_length": "auto",
                "phase": "zero"
            },
            {
                "name" : "highpass",
                "freqs": 2,
                "filter_length": "auto",
                "phase": "zero"
            },
            {
                "name" : "lowpass",
                "freqs": 200,
                "filter_length": "auto",
                "phase": "zero"
            },
            {
                "name" : "bandpass",
                "freqs": [1, 200],
                "filter_length": "auto",
                "phase": "zero"
            }
        ]
        raw = await run_filters(raw, filters)
        
        # epochs = await make_epochs(raw, duration=1)
        
        # Takes a long time to run, so it is commented out for now.
        # epochs, reject_log = await run_autoreject(epochs)
        
        # Takes a long time to run, so it is commented out for now.
        # epochs = await run_ica(epochs)
        
        tasks.append(get_psd_graph(raw, importID, output_path))
        
        tasks.append(SaveEEG(raw, importID, output_path))

        tasks.append(SaveCSV(raw, importID, output_path))

        

        # This is not recommended for signal processing and analysis functions. 
        # Because the order of the tasks is not guaranteed.
        # This is only recommended for tasks that can be run in parallel.
        # For example, creating multiple figures or saving multiple files.
        if tasks:
            await asyncio.gather(*tasks)  # Run all analysis tasks in parallel

        await update_file_runs(analysis_id, importID)

