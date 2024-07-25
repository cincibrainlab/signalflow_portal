from bson import ObjectId
from uuid import UUID
import traceback
from rich.console import Console

console = Console()

import db as flow_db
from AnalysisFlow import analysis_flows

from prefect.deployments import run_deployment

async def deploy_analysis(analysis_id: str, analysis_function: str):
    """
    This function is used to deploy an analysis to the Prefect server.
    """
    console.log(f"Starting deployment for analysis_id: {analysis_id}, function: {analysis_function}")
    
    # Get the flow from the dictionary
    flow_func = analysis_flows.get(analysis_function)
    
    if not flow_func:
        console.log(f"Error: Analysis function '{analysis_function}' not found in analysis_flows")
        raise ValueError(f"Analysis function '{analysis_function}' not found.")
    
    console.log(f"Found flow function: {flow_func.__name__}")
    
    try:
        # Create a deployment for the flow using the new method
        
        deployment = await flow_func.to_deployment(
            name=f"{analysis_function}_deployment_{analysis_id}",
            parameters={"analysis_id": analysis_id},
            work_pool_name="analysis-process-pool",
            job_variables={"working_dir": "./"},
        )
        console.log(f"Deployment created: [yellow]{deployment.name}[/]")

        # Apply the deployment
        deployment_id = await deployment.apply()
        console.log(f"Deployment applied with ID: {deployment_id}")
        
        # Schedule runs for each file in the analysis
        result = await schedule_runs(analysis_id, deployment_id, deployment)
        console.log(result)
        
        return {"success": True, "message": f"Deployed {analysis_function} for analysis_id {analysis_id}", "id": deployment_id}
    except Exception as e:
        console.log(f"Error deploying analysis: {str(e)}")
        console.log(f"Traceback: {traceback.format_exc()}")
        raise

async def schedule_runs(analysis_id: str, deployment_id: UUID, deployment):
    console.log(f"Scheduling runs for analysis_id: {analysis_id}, deployment_id: {deployment_id}")
    db = await flow_db.get_database()
    analysis = await db.EegAnalysis.find_one({"_id": ObjectId(analysis_id)})
    if not analysis:
        console.log(f"Error: Analysis with ID {analysis_id} not found.")
        raise ValueError(f"Analysis with ID {analysis_id} not found.")

    # Convert UUID to string before storing
    deployment_id_str = str(deployment_id)

    # Update the deployment_id in the EegAnalysis document
    update_result = await db.EegAnalysis.update_one(
        {"_id": ObjectId(analysis_id)},
        {"$set": {"deployment_id": deployment_id_str}}
    )
    if update_result.modified_count == 0:
        console.log(f"Warning: Failed to update deployment_id for analysis {analysis_id}")


    for file_id in analysis['valid_files']:
        try:
            file = await db.OriginalImportFile.find_one({"_id": ObjectId(file_id)})
            if not file:
                console.log(f"[bold red]Warning[/]: File with ID {file_id} not found in the database.")
                continue
            
            # await serve(deployment)
            await run_deployment(
                name=deployment_id,
                parameters={
                    "importID": file["upload_id"],
                },
                timeout=0
            )
            console.log(f"Run submitted for file {file_id}")
        except Exception as e:
            console.log(f"[bold red]Error[/]: Error submitting run for file {file_id}: {str(e)}")
            console.log(f"[bold red]Error[/]: Error type: {type(e).__name__}")
            console.log(f"[bold red]Error[/]: Error details: {e.args}")
            continue

    return f"[bold green]Success[/]: Submitted runs for all files in analysis {analysis_id}"