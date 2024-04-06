from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, EEGFileCatalog, DatasetCatalog, UploadCatalog, EegFormat, EegParadigm
from portal_utils import load_config
import logging

db_url = 'postgresql://sfportal:sfportal@localhost:3002/sfportal'

def get_db_session():
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    print("Successfully connected to the database at sfportal database")
    return session

def drop_eeg_file_catalog():
    try:
        engine = create_engine(db_url)
        EEGFileCatalog.__table__.drop(engine)
        logging.info("EEGFileCatalog table dropped successfully.")
    except Exception as e:
        logging.error(f"Failed to drop EEGFileCatalog table: {e}")

def drop_all_tables():
    try:
        engine = create_engine(db_url)
        Base.metadata.drop_all(engine)
        logging.info("All tables dropped successfully.")
    except Exception as e:
        logging.error(f"Failed to drop all tables: {e}")

def generate_eeg_format_and_paradigm():
    """
    Generates EEGFormat and EEGParadigm records from a YAML file.
    
    Args:
        yaml_file (str): Path to the YAML file containing the format and paradigm data.
    """
    session = get_db_session()

    config = load_config()
    
    for format_data in config['eeg_formats']:
        format_name = format_data['format_name']
        description = format_data['description']
        eeg_format = EegFormat(format_name=format_name, description=description)
        session.merge(eeg_format)
    
    for paradigm_data in config['eeg_paradigms']:
        paradigm_name = paradigm_data['paradigm_name']
        description = paradigm_data['description']
        eeg_paradigm = EegParadigm(paradigm_name=paradigm_name, description=description)
        session.merge(eeg_paradigm)
    
    session.commit()      