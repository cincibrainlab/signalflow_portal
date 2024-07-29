# Standard library imports
import asyncio
import sys
# Signalflow imports
sys.path.append("builds/backend")
import db as flow_db
sys.path.append("builds/backend/PrefectCode/AnalysisFlow/")
from PrefectCode import UtilityTasks 
# Third-party library imports
from prefect import flow, task
import mne
from bson import ObjectId
import matlab.engine

@flow(name="ComputePsdAnalysisMatlab_Flow", description="Run a Template analysis on the file.")
async def ComputePsdAnalysisMatlab_Flow(importID: str, analysis_function: str, analysis_id: str):
    config = await UtilityTasks.loadconfig()  # Load configuration file
    upload_path = config["folder_paths"]["uploads"]  # Get upload directory path

    db = await flow_db.get_database()
    
    # Get data from the database about the analysis
    EEGAnalysis = await db.EegAnalysis.find_one({"_id": ObjectId(analysis_id)})
    
    # Get the analysis function from the database
    AnalysisFunction = await db.AnalysisFunction.find_one({"name": analysis_function})
    output_path = AnalysisFunction["output_path"]
    
    # Get the file from the database
    original_file = await db.OriginalImportFile.find_one({"upload_id": importID})
    upload_id = original_file["upload_id"]
    
    # Import the file
    raw_eeg = await UtilityTasks.getRaw(upload_id, upload_path)
    
    if raw_eeg is not None:
        raw = raw_eeg
        # Perform Preprocessing here
        
        eng = matlab.engine.start_matlab()
        x = 4.0
        eng.workspace['y'] = x
        y = eng.eval('sqrt(y)')
        print(y)

        # This will run all the tasks listed in parallel. Vastly speeds up code execution.
        # This is not recommended for signal processing and analysis functions. 
        # Because the order of the tasks is not guaranteed.
        # This is only recommended for tasks that can be run in parallel.
        # For example, creating multiple figures or saving multiple files.
        tasks = []
        if tasks:
            await asyncio.gather(*tasks)  # Run all analysis tasks in parallel