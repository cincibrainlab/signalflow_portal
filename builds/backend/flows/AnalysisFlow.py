# Standard library imports
import os
# Third-party library imports
from prefect import flow

output_path: str = "portal_files/output"
# prefect work-pool create analysis-process-pool
# prefect worker start --pool analysis-process-pool

@flow(name="FakeAnalysis", description="Run a fake analysis on the file.")
async def fakeAnalysis(importID: str, analysis_id: str):
    
    # TODO: 

    analysisName = "Fake Analysis"
    savePath = os.path.join(output_path, (analysisName + "_" + importID))
    print(f"Running analysis on file {importID}")

    with open(savePath, 'a') as file:
        file.write(f"Ran {analysisName} on {importID}\n")

analysis_flows = {
    "fakeAnalysis": fakeAnalysis,
    "fakeAnalysis2": fakeAnalysis,
    # Add more flows here as needed
}