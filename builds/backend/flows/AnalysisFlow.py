# Standard library imports
import os
import asyncio
from bson import ObjectId
from uuid import UUID
import traceback

# Third-party library imports
from prefect import flow
from prefect.deployments import run_deployment
from flows import AnalysisTasks as tasks
import db as flow_db

@flow(name="FakeAnalysis", description="Run a fake analysis on the file.")
async def fakeAnalysis(importID: str, output_path: str = "portal_files/output"):

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

async def deploy_analysis(analysis_id: str, analysis_function: str):
    """
    This function is used to deploy an analysis to the Prefect server.
    """
    print(f"Starting deployment for analysis_id: {analysis_id}, function: {analysis_function}")
    
    # Get the flow from the dictionary
    flow_func = analysis_flows.get(analysis_function)
    
    if not flow_func:
        print(f"Error: Analysis function '{analysis_function}' not found in analysis_flows")
        raise ValueError(f"Analysis function '{analysis_function}' not found.")
    
    print(f"Found flow function: {flow_func.__name__}")
    
    try:
        print("Creating deployment")
        # Create a deployment for the flow using the new method
        deployment = await flow_func.to_deployment(
            name=f"{analysis_function}_deployment_{analysis_id}",
            parameters={"analysis_id": analysis_id},
            work_pool_name="analysis-process-pool",
        )
        print(f"Deployment created: {deployment}")
        
        print("Applying deployment")
        # Apply the deployment
        deployment_id = await deployment.apply()
        print(f"Deployment applied with ID: {deployment_id}")
        
        print("Scheduling runs")
        # Schedule runs for each file in the analysis
        await schedule_runs(analysis_id, deployment_id)
        print("Runs scheduled successfully")
        
        return {"success": True, "message": f"Deployed {analysis_function} for analysis_id {analysis_id}", "id": deployment_id}
    except Exception as e:
        print(f"Error deploying analysis: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise



async def schedule_runs(analysis_id: str, deployment_id: UUID):
    print(f"Scheduling runs for analysis_id: {analysis_id}, deployment_id: {deployment_id}")
    db = await flow_db.get_database()
    analysis = await db.EegAnalysis.find_one({"_id": ObjectId(analysis_id)})
    if not analysis:
        print(f"Error: Analysis with ID {analysis_id} not found.")
        raise ValueError(f"Analysis with ID {analysis_id} not found.")

    # Convert UUID to string before storing
    deployment_id_str = str(deployment_id)

    # Update the deployment_id in the EegAnalysis document
    update_result = await db.EegAnalysis.update_one(
        {"_id": ObjectId(analysis_id)},
        {"$set": {"deployment_id": deployment_id_str}}
    )
    if update_result.modified_count == 0:
        print(f"Warning: Failed to update deployment_id for analysis {analysis_id}")
    else:
        print(f"Updated deployment_id for analysis {analysis_id}")

    for file_id in analysis['valid_files']:
        try:
            file = await db.OriginalImportFile.find_one({"_id": ObjectId(file_id)})
            if not file:
                print(f"Warning: File with ID {file_id} not found in the database.")
                continue

            print(f"Submitting run for file {file_id}")
            await run_deployment(
                name=deployment_id,
                parameters={
                    "importID": file["upload_id"],
                },
                timeout=0
            )
            print(f"Run submitted for file {file_id}")
        except Exception as e:
            print(f"Error submitting run for file {file_id}: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error details: {e.args}")
            continue

    return f"Submitted runs for all files in analysis {analysis_id}"

if __name__ == "__main__":
    import asyncio
    import AnalysisTasks as tasks
    
    async def main():
        result = await deploy_analysis("some_analysis_id", "fakeAnalysis", {"example_num": 42})
        print(result)
    
    asyncio.run(main())