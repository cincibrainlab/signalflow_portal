from fastapi import APIRouter
import logging
import signalfloweeg.portal as portal


router = APIRouter()

@router.get("/api/test")
def test():
    logging.info("Test endpoint was called. SignalFlowEEG API is up and running!")
    return {"message": "SignalFlowEEG API is up and running!"}

@router.get("/api/drop-tables")
def api_drop_all_tables():
    result = portal.db_utilities.drop_all_tables()
    return {"message": result["message"]}

@router.get("/api/clear-dataset-table")
def api_clear_dataset_table():
    logging.info("Clearing dataset table...")
    portal.db_datasets.clear_table_dataset()
    logging.info("Dataset table cleared successfully.")
    return {"message": "Dataset table cleared."}

@router.get("/api/clear-table/{table_name}")
def api_clear_table(table_name: str):
    logging.info(f"Attempting to clear table: {table_name}")
    try:
        portal.db_utilities.drop_table(table_name)
        #portal.db_datasets.clear_table(table_name)
        return {"message": f"Table {table_name} cleared successfully."}
    except Exception as e:
        logging.error(f"Error clearing table {table_name}: {str(e)}")
        return {"error": f"Error clearing table {table_name}: {str(e)}"}


@router.get("/api/load-channels-paradigms2")
def load_channels_paradigms():
    config = portal.portal_utils.load_config()

    def check_and_add(session, model, name, description):
        if not session.query(model).filter_by(name=name).first():
            session.add(model(name=name, description=description))

    def generate_records(session, data, model, title):
        from rich.console import Console
        from rich.table import Table
        console = Console()
        table = Table(title=f"[bold]{title}[/bold]")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")

        for item in data:
            check_and_add(session, model, item['name'], item['description'])
            table.add_row(item['name'], item['description'])

        console.print(table)
        console.print()


    config = portal.portal_utils.load_config()

    with portal.sessionmaker.get_db() as session:
        generate_records(session, config['eeg_formats'], portal.models.EegFormat, "EEG Formats")
        generate_records(session, config['eeg_paradigms'], portal.models.EegParadigm, "EEG Paradigms")
        session.commit()

    return {"message": config}