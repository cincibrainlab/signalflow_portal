# Standard library imports
import asyncio
# Third-party library imports
from prefect import flow, task
import db as flow_db
from AnalysisTasks import getRaw

output_path: str = "portal_files/output"
# prefect work-pool create analysis-process-pool
# prefect worker start --pool analysis-process-pool

@task(retries=1)
async def loadconfig():
    # Load configuration file
    config = await flow_db.load_config()
    return config

@flow(name="FakeAnalysis", description="Run a fake analysis on the file.")
async def fakeAnalysis(importID: str, analysis_id: str):
    config = await loadconfig()  # Load configuration file
    upload_path = config["folder_paths"]["uploads"]  # Get upload directory path
    output_path = config["folder_paths"]["output"]  # Get output directory path

    db = await flow_db.get_database()
    test_file = await db.OriginalImportFile.find_one({"upload_id": importID})
    upload_id = test_file["upload_id"]
    tasks = []

    raw_eeg = await getRaw(upload_id, upload_path)
    print(raw_eeg)
    
    if raw_eeg is not None:
        raw = raw_eeg
        # Perform analysis here
        raw.notch_filter(freqs=20, filter_length='auto', phase='zero') # just so its super obvious 
        
        psd = raw.compute_psd(fmin=1, fmax=50)
        
        fig = psd.plot(show=False)
        
        fig.savefig(f"{output_path}/psd_{importID}.png")
        
        
        # Save output to output directory
    

    if tasks:
        await asyncio.gather(*tasks)  # Run all analysis tasks in parallel

analysis_flows = {
    "fakeAnalysis": fakeAnalysis,
    "fakeAnalysis2": fakeAnalysis,
    # Add more flows here as needed
}