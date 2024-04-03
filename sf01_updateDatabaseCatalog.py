from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

import os
import glob
import json
import logging

import mne

# Configure the logger
logging.basicConfig(
    filename='portal_files/logs/eeg_file_catalog.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

db_url = 'postgresql://sfportal:sfportal@localhost:3002/sfportal'

# Set up the SQLAlchemy engine and Session
Base = declarative_base()

class EEGFileCatalog(Base):
    __tablename__ = 'eeg_file_catalog'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    dataset_name = Column(String)
    storage = Column(Text, unique=True)
    upload_id = Column(String, unique=True)
    size = Column(String)
    dataset_id = Column(Integer)
    hash = Column(String)

class DatasetCatalog(Base):
    __tablename__ = 'dataset_catalog'
    id = Column(Integer, primary_key=True)
    dataset_name = Column(String, unique=True)
    description = Column(Text)
    eeg_format = Column(Integer)
    is_event_related = Column(Integer)
    

def drop_EEGFileCatalog():
    try:
        engine = create_engine(db_url)
        Base.metadata.drop_all(engine)
        logging.info("All tables dropped successfully.")
    except Exception as e:
        logging.error(f"Failed to drop EEGFileCatalog table: {e}")

def get_db_session():
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)  # This line creates all tables
    Session = sessionmaker(bind=engine)
    session = Session()
    print("Successfully connected to the database at sfportal database")
    return session

def ingest_uploads():
    print("catalog_eeg_files() path: ", os.getcwd())
    folder_path = './portal_files/uploads/'  # Replace with the actual folder path
    info_files = glob.glob(os.path.join(folder_path, '*.info'))

    def create_file_hash(file_path):
        import hashlib
        hash_blake2 = hashlib.blake2b()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_blake2.update(chunk)
        return hash_blake2.hexdigest()

    def extract_metadata(info_file):
        with open(info_file, 'r') as f:
            file_metadata = json.load(f)
            row = {
                'dataset_name': file_metadata['MetaData'].get('datasetName', 'NA'),
                'upload_id': file_metadata.get('ID', 'NA'),
                'size': file_metadata.get('Size', 'NA'),
                'storage': file_metadata['Storage'].get('Path', 'NA'),
                'filename': file_metadata['MetaData'].get('filename', 'NA'),
                'hash': create_file_hash(os.path.join(folder_path,file_metadata.get('ID', 'NA')))
            }
        return row

    def add_metadata_to_db(info_files):
        session = get_db_session()
        for info_file in info_files:
            row = extract_metadata(info_file)
            dataset_name = row['dataset_name']
            dataset = session.query(DatasetCatalog).filter_by(dataset_name=dataset_name).first()
            if not dataset:
                dataset = DatasetCatalog(dataset_name=dataset_name)
                session.add(dataset)
            eeg_file = EEGFileCatalog(dataset_id=dataset.id, **row)
            session.merge(eeg_file)
            logging.info(f"Metadata added to database for file: {row['filename']}")
        session.commit()
        session.close()

    add_metadata_to_db(info_files)

if __name__ == "__main__":
    get_db_session()
    drop_EEGFileCatalog()
    ingest_uploads()

