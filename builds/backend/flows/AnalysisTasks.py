import time
from bson import ObjectId

from prefect import task
import db as flow_db
import mne
import json
import os
import logging
from datetime import datetime
import asyncio


@task(name="get_db", retries=2)
async def get_db():
    return await flow_db.get_database()

@task(name="get_file")
async def get_files(analysis_id):
    db = await get_db()
    analysis_id = ObjectId(analysis_id)
    analysis_data = await db.EegAnalysis.find_one({"_id": analysis_id})
    file_ids = analysis_data["files"]

    file_dict_list = []
    for id in file_ids:
        file = await db.File.find_one({"_id": id})
        if not file:
            return {"error": "File not found"}
        
        file_dict_list.append(file)
    if not file_dict_list:
        time.sleep(2)
        raise "no files found"
    return file_dict_list

@task
async def getRaw(upload_id: str, upload_path: str):
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
        
        # Read EEGLAB file info 
        eeg_data = await asyncio.to_thread(mne.io.read_raw_eeglab, set_dest_path, preload=True, verbose=True)
        
        if os.path.exists(set_dest_path):
            await asyncio.to_thread(os.remove, set_dest_path)
            logging.info(f"Removed SET file {set_dest_path}")
        if fdt_dest_path and os.path.exists(fdt_dest_path):
            await asyncio.to_thread(os.remove, fdt_dest_path)
            logging.info(f"Removed FDT file {fdt_dest_path}")
        
        return eeg_data
    
    except Exception as e:
        logging.error(f"Exception occurred when creating EEG Obj: {str(e)}")
        logging.error(f"File path: {set_dest_path}")
        logging.error(f"File exists: {os.path.exists(set_dest_path)}")
        if os.path.exists(set_dest_path):
            with open(set_dest_path, 'rb') as f:
                logging.error(f"File size: {len(f.read())} bytes")
        raise


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