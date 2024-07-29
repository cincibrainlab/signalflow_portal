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

@task(name="getRawMatlab", retries=1, description="")
async def getRawMatlab(eng ,upload_id: str, upload_path: str):
    """
    This function is used to get the EEG data from the specified upload path. 

    Parameters:
    upload_id (str): The ID of the upload.
    upload_path (str): The path where the upload is located.

    Returns:
    eeg_data: The EEG data (either raw or epoched).
    """

    try: 
        set_dest_path, fdt_dest_path = await flow_db.copy_import_files(upload_id)
        
        print(f"SET file path: {set_dest_path}")
        print(f"FDT file path: {fdt_dest_path}")
        
        if fdt_dest_path is not None:
            eng.eval('EEG = pop_loadset(\''+ set_dest_path +'\');', nargout=0)
            
    except Exception as e:
        logging.error(f"Exception occurred when creating EEG Obj: {str(e)}")
        logging.error(f"File path: {set_dest_path}")
        logging.error(f"File exists: {os.path.exists(set_dest_path)}")
        if os.path.exists(set_dest_path):
            with open(set_dest_path, 'rb') as f:
                logging.error(f"File size: {len(f.read())} bytes")
        raise

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
    
    # Start the Matlab engine
    eng = matlab.engine.start_matlab()
    # eng.addpath(r'builds/backend/PrefectCode/matlab/eeglab/')
    eng.eval("eeglab('nogui')")
    
    # Import the file - Will save as 'EEG' in the Matlab workspace
    await getRawMatlab(eng, upload_id, upload_path)

    # Perform Preprocessing here
    eng.eval('[spectra, freqs] = spectopo(EEG.data, 0, EEG.srate);', nargout=0)
    eng.eval("fig = figure('visible', 'off');", nargout=0)
    eng.eval('plot(freqs, spectra);', nargout=0)
    eng.eval('title("Power Spectral Density");', nargout=0)
    eng.eval('xlabel("Frequency (Hz)");', nargout=0)
    eng.eval('ylabel("Power/Frequency (dB/Hz)");', nargout=0)
    eng.eval('saveas(fig, "portal_files/output/psd.png");', nargout=0)
    

    # This will run all the tasks listed in parallel. Vastly speeds up code execution.
    # This is not recommended for signal processing and analysis functions. 
    # Because the order of the tasks is not guaranteed.
    # This is only recommended for tasks that can be run in parallel.
    # For example, creating multiple figures or saving multiple files.
    tasks = []
    if tasks:
        await asyncio.gather(*tasks)  # Run all analysis tasks in parallel