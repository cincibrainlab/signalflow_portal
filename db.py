from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, EEGFileCatalog, DatasetCatalog, UploadCatalog
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