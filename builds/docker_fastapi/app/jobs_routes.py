from fastapi import APIRouter
import logging
import signalfloweeg.portal as portal
from fastapi import BackgroundTasks, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/api/get-import-ids")
def get_import_ids():
    logging.info("Getting import IDs...")
    import_ids = portal.import_catalog.get_import_ids()
    return import_ids


@router.get("/api/gen-job-list")
def generate_joblist():
    logging.info("Generating job list...")
    job_list = portal.import_catalog.generate_joblist()
    return job_list


@router.post("/api/trigger_analysis/{upload_id}")
async def trigger_analysis(
    upload_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(portal.sessionmaker.get_db),
):
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title=f"Triggering Analysis for Upload ID: {upload_id}")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta", no_wrap=True)

    import_info = portal.sessionmaker.get_import_info(upload_id)
    if "error" in import_info:
        table.add_row("Error", import_info["error"])
    else:
        for key, value in import_info.items():
            table.add_row(key, str(value))

    console.print(table)

    # Placeholder for background task to start analysis
    return {"message": "Analysis triggered"}


@router.get("/api/show_upload_catalog")
def list_upload_catalog():
    from rich.console import Console
    from rich.table import Table

    logging.info("Getting Upload Catalog Info")
    upload_catalog = portal.sessionmaker.get_upload_catalog()

    console = Console()
    table = Table(title="Upload Catalog")
    table.add_column("Upload_ID", style="cyan", no_wrap=True)
    table.add_column("FDT Upload", style="green", no_wrap=True)
    table.add_column("FileName", style="magenta", no_wrap=True)
    table.add_column("is_set_file", style="green", no_wrap=True)
    table.add_column("has_fdt_file", style="magenta", no_wrap=True)
    table.add_column("fdt_filename", style="green", no_wrap=True)
    for upload in upload_catalog:
        table.add_row(
            upload["upload_id"],
            upload["fdt_id"],
            upload["original_name"],
            str(upload["is_set_file"]),
            str(upload["has_fdt_file"]),
            upload["fdt_filename"],
        )

    console.print(table)
    return upload_catalog


@router.get("/api/get-eligible-files")
def list_eligible_files():
    logging.info("Getting eligible files...")
    eligible_files = portal.sessionmaker.get_eligible_files()
    return eligible_files
