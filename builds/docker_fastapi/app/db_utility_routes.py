from fastapi import APIRouter
import logging
from signalfloweeg.portal.sessionmaker import get_db
from signalfloweeg.portal.db_utilities import drop_all_tables
from signalfloweeg.portal.models import EegFormat, EegParadigm
from signalfloweeg.portal.portal_utils import load_config
from rich.console import Console
from rich.table import Table


router = APIRouter()

@router.get("/api/test")
def test():
    logging.info("Test endpoint was called. SignalFlowEEG API is up and running!")
    return {"message": "SignalFlowEEG API is up and running!"}

@router.get("/api/drop-tables")
def api_drop_all_tables():
    result = drop_all_tables()
    return {"message": result["message"]}

@router.get("/api/load-channels-paradigms2")
def load_channels_paradigms():
    config = load_config()

    def check_and_add(session, model, name, description):
        if not session.query(model).filter_by(name=name).first():
            session.add(model(name=name, description=description))

    def generate_records(session, data, model, title):
        table = Table(title=f"[bold]{title}[/bold]")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")

        for item in data:
            check_and_add(session, model, item['name'], item['description'])
            table.add_row(item['name'], item['description'])

        console.print(table)
        console.print()

    console = Console()
    config = load_config()

    with get_db() as session:
        generate_records(session, config['eeg_formats'], EegFormat, "EEG Formats")
        generate_records(session, config['eeg_paradigms'], EegParadigm, "EEG Paradigms")
        session.commit()

    return {"message": config}