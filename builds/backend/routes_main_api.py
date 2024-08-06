from fastapi import APIRouter, HTTPException
import logging
import db as flow_db
import os
# from fastapi.responses import JSONResponse
from PrefectCode.UtilityFuncs import deploy_analysis
from prefect.client import get_client
from prefect.client.schemas.filters import DeploymentFilter
from datetime import timedelta
from entrypoint import check_entrypoint
from typing import List
import models
from pydantic import BaseModel
import io
from fastapi.responses import StreamingResponse
import numpy as np
import zlib
import asyncio

from fastapi import Response
import zipfile

router = APIRouter()



# ────────────────────────────────────────────────────────────────────────────────
# UNIVERSAL TEST
# ────────────────────────────────────────────────────────────────────────────────
@router.get("/api/test")
async def test():
    return {"message": "API Test Successful."}

# ───────────────────────────────────────────────────────────────────────────────
# CONFIGURATION CALLS
# ───────────────────────────────────────────────────────────────────────────────
@router.get("/api/get-portal-paths")
async def get_portal_paths():
    paths = await flow_db.get_folder_paths()
    return {"message": paths}

# ───────────────────────────────────────────────────────────────────────────────
# DATABASE: SERVICE UTILITIES
# ────────────────────────────────────────────────────────────────────────────────
  
@router.get("/api/check-db-connection", status_code=200)
async def check_database_connection():
    if not await flow_db.is_database_connected():
        raise HTTPException(status_code=503, detail="Database is not connected")
    return {"message": "Database is connected"}

@router.get("/api/delete-database")
async def delete_database():
    await flow_db.delete_database()
    return {"message": "Database deleted successfully"}

@router.get("/api/load-database-summary")
async def load_database_summary():
    logging.info("Loading database summary...")
    summary = await flow_db.generate_database_summary()
    return {"message": summary}

@router.get("/api/reset_portal")
async def api_reset_portal():
    logging.info("Resetting portal...")
    logging.info("Cleaning up uploads folder and resetting database...")
    from rich.console import Console

    console = Console()
    # Clean up uploads folder
    if await flow_db.is_config_table_present():
        console.print("ConfigDB table is present. Resetting upload folder...")
        UPLOAD_PATH = (await flow_db.get_folder_paths())["uploads"]
        console.print(f"Cleaning up uploads folder: {UPLOAD_PATH}")

        import shutil
        try:
            file_count = 0
            for filename in os.listdir(UPLOAD_PATH):
                file_path = os.path.join(UPLOAD_PATH, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    file_count += 1
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    file_count += 1
            console.print(f"All files in the uploads folder have been removed. Total files deleted: {file_count}")
        except Exception as e:
            console.print(f"Error occurred while deleting files in the uploads folder: {e}")
    await flow_db.initialize_database(reset=True)
    await check_entrypoint(console)

    return {"message": "Uploads Removed and Portal Reset Successfully."}

# ───────────────────────────────────────────────────────────────────────────────
# WEBFORMS: CONTACT TAB
# ───────────────────────────────────────────────────────────────────────────────'

class FileAssignmentRequest(BaseModel):
    name: str
    email: str
    message: str

@router.post("/api/sendContactMessage")
async def send_contact_message(request: FileAssignmentRequest):
    # We either need to setup a smtp server, use a third party service like sendgrid, or make it a github issue
    # For now, we will just log the message
    name = request.name
    email = request.email
    message = request.message
    print(f"Contact Message: {name} - {email} - {message}")

# ───────────────────────────────────────────────────────────────────────────────
# WEBFORMS: UPLOAD TAB
# ───────────────────────────────────────────────────────────────────────────────
@router.get("/api/list-eeg-formats", response_model=List[models.EEGFormat])
async def list_eeg_formats():
    formats = await flow_db.get_eeg_formats()
    logging.debug(f"EEG Formats: {formats}")
    return [models.EEGFormat(**format) for format in formats]

@router.get("/api/list-eeg-paradigms", response_model=List[models.EEGParadigm])
async def list_eeg_paradigms():
    paradigms = await flow_db.get_eeg_paradigms()
    logging.debug(f"EEG Paradigms: {paradigms}")
    return [models.EEGParadigm(**paradigm) for paradigm in paradigms]

@router.get("/api/list-analysis-flows", response_model=List[models.AnalysisFlow])
async def list_analysis_flows():
    flows = await flow_db.get_analysis_flows()
    logging.debug(f"Analysis Flows: {flows}")
    return [models.AnalysisFlow(**flow) for flow in flows]

# ───────────────────────────────────────────────────────────────────────────────
# WEBFORMS: FILES TAB
# ────────────────────────────────────────────────────────────────────────────────
@router.get("/api/get-original-file-catalog")
async def get_original_file_catalog():
    logging.info("Getting file table...")
    file_catalog = await flow_db.get_OriginalImportFile()
    return [models.OriginalImportFile(**upload) for upload in file_catalog]

@router.get("/api/get-original-file-from-upload-id/{fileObjectId}")
async def get_original_file_from_upload_id(fileObjectId: str):
    try:
        file = await flow_db.get_OriginalImportFile_by_id(fileObjectId)
        logging.debug(f"File: {file}")
        return models.OriginalImportFile(**file)
    except Exception as e:
        logging.error(f"Error retrieving file: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/get-matching-files")
async def get_matching_files(valid_formats: list[str], valid_paradigms: list[str]):
    logging.info("Getting file table...")
    file_catalog = await flow_db.get_matchingFiles(valid_formats, valid_paradigms)
    return [models.OriginalImportFile(**upload) for upload in file_catalog]

@router.get("/api/get-participants")
async def get_participants():
    logging.info("Getting participants...")
    participants = await flow_db.get_participants()
    return [models.Participant(**participant) for participant in participants]

@router.get("/api/get-form-options/{form_name}")
async def get_form_options(form_name: str):
    logging.info("Getting form options...")
    form_options = await flow_db.get_form_options(form_name)
    return models.FormInfo(**form_options)

class FileAssignmentRequest(BaseModel):
    ID: str
    fileId: str
    
@router.post("/api/assign-participant-to-file",response_model=models.OriginalImportFile)
async def assign_participant_to_file(request: FileAssignmentRequest):
    try:
        updated_file = await flow_db.assign_participant_to_file(request.ID, request.fileId)
        logging.debug(f"File Updated: {updated_file}")
        return {"success": True, "message": "Participant assigned to file successfully", "file": updated_file}
    except Exception as e:
        logging.error(f"Error assigning participant to file: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/api/assign-eeg-format-to-file",response_model=models.OriginalImportFile)
async def assign_eeg_format_to_file(request: FileAssignmentRequest):
    try:
        updated_file = await flow_db.assign_eeg_format_to_file(request.ID, request.fileId)
        logging.debug(f"File Updated: {updated_file}")
        return {"success": True, "message": "EEG Format assigned to file successfully", "file": updated_file}
    except Exception as e:
        logging.error(f"Error assigning EEG Format to file: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/api/assign-eeg-paradigm-to-file",response_model=models.OriginalImportFile)
async def assign_eeg_paradigm_to_file(request: FileAssignmentRequest):
    try:
        updated_file = await flow_db.assign_eeg_paradigm_to_file(request.ID, request.fileId)
        logging.debug(f"File Updated: {updated_file}")
        return {"success": True, "message": "EEG Paradigm assigned to file successfully", "file": updated_file}
    except Exception as e:
        logging.error(f"Error assigning EEG Paradigm to file: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/api/assign-tags-to-file/{fileId}")
async def assign_tags_to_file(fileId: str, tags: list[str]):
    try:
        updated_file = await flow_db.assign_tags_to_file(tags, fileId)
        logging.debug(f"File Updated: {updated_file}")
        return {"success": True, "message": "Tags assigned to file successfully", "file": updated_file}
    except Exception as e:
        logging.error(f"Error assigning tags to file: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/get-participant/{participantObjectId}")
async def get_participant(participantObjectId: str):
    try:
        participant = await flow_db.get_participant(participantObjectId)
        logging.debug(f"Participant: {participant}")
        return {"success": True, "message": "Participant retrieved successfully", "participant": participant}
    except Exception as e:
        logging.error(f"Error retrieving participant: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/api/get-analysis-from-deployment-id/{DeploymentID}")
async def get_analysis_from_deployment_id(DeploymentID: str):
    try:
        analysis = await flow_db.get_analysis_from_deployment_id(DeploymentID)
        logging.debug(f"Analysis: {analysis}")
        return models.EegAnalysis(**analysis)
    except Exception as e:
        logging.error(f"Error retrieving analysis: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/api/get-analysis-flow/{AnalysisID}")
async def get_analysis(AnalysisID: str):
    try:
        analysisFlow = await flow_db.get_analysisFlow(AnalysisID)
        logging.debug(f"Analysis: {analysisFlow}")
        return models.AnalysisFlow(**analysisFlow)
    except Exception as e:
        logging.error(f"Error retrieving analysis: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
    
@router.get("/api/get-eeg-format/{FormatObjectID}")
async def get_eeg_format(FormatObjectID: str):
    try:
        eeg_format = await flow_db.get_eeg_format(FormatObjectID)
        logging.debug(f"EEG Format: {eeg_format}")
        return {"success": True, "message": "EEG Format retrieved successfully", "eeg_format": eeg_format}
    except Exception as e:
        logging.error(f"Error retrieving EEG Format: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/api/get-eeg-paradigm/{ParadigmObjectID}")
async def get_eeg_paradigm(ParadigmObjectID: str):
    try:
        eeg_paradigm = await flow_db.get_eeg_paradigm(ParadigmObjectID)
        logging.debug(f"EEG Paradigm: {eeg_paradigm}")
        return {"success": True, "message": "EEG Paradigm retrieved successfully", "eeg_paradigm": eeg_paradigm}
    except Exception as e:
        logging.error(f"Error retrieving EEG Paradigm: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

@router.get("api/get-tags/{fileId}")
async def get_tags(fileId: str):
    try:
        tags = await flow_db.get_tags(fileId)
        logging.debug(f"Tags: {tags}")
        return {"success": True, "message": "Tags retrieved successfully", "tags": tags}
    except Exception as e:
        logging.error(f"Error retrieving tags: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/api/add-participant", response_model=models.Participant)
async def add_participant(participant: models.Participant):
    try:
        new_participant = await flow_db.add_participant(participant)
        logging.debug(f"New Participant Added: {new_participant}")
        return {"success": True, "message": "Participant added successfully", "participant": new_participant}
    except Exception as e:
        logging.error(f"Error adding participant: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/api/add-analysis")
async def add_analysis(analysis: models.EegAnalysis):
    try:
        new_analysis = await flow_db.add_analysis(analysis)
        logging.debug(f"New analysis Added to db: {new_analysis}")
        deployment = await deploy_analysis(new_analysis["id"], new_analysis["analysis_flow"])
        logging.debug(f"New analysis Deployed: {deployment}")
        return {"success": True, "message": "Analysis added and deployed successfully", "analysisId" : new_analysis["id"], "deployment_id": deployment["id"]}
    except Exception as e:
        logging.error(f"Error adding analysis: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/get-analyses")
async def get_analyses():
    try:
        analyses = await flow_db.get_analyses()
        logging.info(f"Retrieved {len(analyses)} analyses")
        return analyses
    except Exception as e:
        logging.error(f"Error in get_analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/api/get-file-runs/{original_file_id}")
async def get_file_runs(original_file_id: str):
    try:
        file_runs = await flow_db.get_file_runs(original_file_id)
        logging.info(f"Retrieved file runs: {file_runs}")
        return file_runs
    except Exception as e:
        logging.error(f"Error in get_file_runs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/api/get-file-run/{file_run_id}")
async def get_file_run(file_run_id: str):
    try:
        file_run = await flow_db.get_file_run(file_run_id)
        logging.info(f"Retrieved file run: {file_run}")
        return file_run
    except Exception as e:
        logging.error(f"Error in get_file_runs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ───────────────────────────────────────────────────────────────────────────────
# FUNCTION: DATASET CRUD
# ────────────────────────────────────────────────────────────────────────────────


# ────────────────────────────────────────────────────────────────────────────────
# FUNCTION: UPLOAD PROCESSING
# ────────────────────────────────────────────────────────────────────────────────
@router.get("/api/process-uploads")
async def process_uploads():
    logging.info("Processing new uploads...")
    UPLOAD_PATH = (await flow_db.get_folder_paths())["uploads"]
    logging.info(f"UPLOAD_PATH: {UPLOAD_PATH}")
    await flow_db.process_new_uploads(upload_dir=UPLOAD_PATH)
    return {"message": "Uploads processed successfully."}

# ────────────────────────────────────────────────────────────────────────────────
# FUNCTION: PREFECT
# ────────────────────────────────────────────────────────────────────────────────

@router.get("/prefect/prefect-stats/{deploymentId}")
async def get_prefect_stats(deploymentId: str):
    try:
        async with get_client() as client:
            deployment_filter = DeploymentFilter(id={"any_": [deploymentId]})
            flow_runs = await client.read_flow_runs(deployment_filter=deployment_filter)
            
            total_runs = len(flow_runs)
            completed_runs = sum(1 for run in flow_runs if run.state.is_completed())
            failed_runs = sum(1 for run in flow_runs if run.state.is_failed())
            pending_runs = total_runs - completed_runs - failed_runs
            
            completed_durations = [run.end_time - run.start_time for run in flow_runs if run.state.is_completed() and run.end_time and run.start_time]
            avg_runtime = sum(completed_durations, timedelta()) / len(completed_durations) if completed_durations else timedelta()
            
            response = {
                "deployment_id": deploymentId,
                "total_runs": total_runs,
                "completed_runs": completed_runs,
                "failed_runs": failed_runs,
                "pending_runs": pending_runs,
                "avg_runtime": str(avg_runtime),
                "completion_rate": (completed_runs / total_runs) * 100 if total_runs > 0 else 0,
                "success_rate": (completed_runs / (completed_runs + failed_runs)) * 100 if (completed_runs + failed_runs) > 0 else 0,
                "runs": [{"id": run.state_id, "status": run.state_type, "name": run.name} for run in flow_runs]
            }
            
            logging.info(f"Prefect stats response for deployment {deploymentId}: {response}")
            return response
    except Exception as e:
        logging.error(f"Error in get_prefect_stats for deployment {deploymentId}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/get-eeg-data/{upload_id}/{sample_rate}")
async def get_EEG_Data(upload_id, sample_rate):
    # try:
    raw_data, psdPath = await flow_db.get_EEG_Data(upload_id)
    
    # Resample to 250 Hz
    raw_data = raw_data.resample(sample_rate)
    
    # Do a .5 hz high pass filter
    raw_data = raw_data.filter(0.5, None)
    
    data = raw_data.get_data()
    bytes_io = io.BytesIO()
    np.save(bytes_io, data, allow_pickle=False)
    
    # Compress
    compressed = zlib.compress(bytes_io.getvalue())
    
    # Create a generator to stream the data
    def iterfile():
        yield compressed
    
    headers = {
        "X-Psd-Path": psdPath,
        "Access-Control-Expose-Headers": "X-Psd-Path"
    }
    
    return StreamingResponse(
        iterfile(),
        media_type="application/octet-stream",
        headers=headers
    )

@router.get("/api/get-eeg-data-shape/{upload_id}")
async def get_EEG_Data_Shape(upload_id):
    # Will return the shape of the data and the sampling frequency
    raw_data, psdPath = await flow_db.get_EEG_Data(upload_id)
    data = raw_data.get_data()
    return {
        "shape": data.shape,
        "sfreq": raw_data.info["sfreq"]
    }


@router.get("/api/download-eeg-file/{upload_id}")
async def download_EEG_Data(upload_id):
    primary_dest_path, secondary_dest_path = await flow_db.copy_import_files(upload_id)
    
    if not (os.path.exists(primary_dest_path) and os.path.exists(secondary_dest_path)):
        return Response(content="One or both files not found", status_code=404)
    
    zip_filename = "downloaded_files.zip"
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(primary_dest_path, os.path.basename(primary_dest_path))
        zip_file.write(secondary_dest_path, os.path.basename(secondary_dest_path))
    
    zip_buffer.seek(0)
    
    if os.path.exists(primary_dest_path):
        await asyncio.to_thread(os.remove, primary_dest_path)
        logging.info(f"Removed SET file {primary_dest_path}")
    if secondary_dest_path and os.path.exists(secondary_dest_path):
        await asyncio.to_thread(os.remove, secondary_dest_path)
        logging.info(f"Removed FDT file {secondary_dest_path}")
    
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment;filename={zip_filename}"}
    )