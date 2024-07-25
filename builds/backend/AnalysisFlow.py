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
# 1000_6_to_1100_9_aaebci_NS_09-05-2023_20230905_121427.set
    db = await flow_db.get_database()
    test_file = await db.OriginalImportFile.find_one({"upload_id": importID})
    upload_id = test_file["upload_id"]
    tasks = []

    raw_eeg = await getRaw(upload_id, upload_path)
    print(raw_eeg)
    

    if tasks:
        await asyncio.gather(*tasks)  # Run all analysis tasks in parallel

analysis_flows = {
    "fakeAnalysis": fakeAnalysis,
    "fakeAnalysis2": fakeAnalysis,
    # Add more flows here as needed
}