import os
import glob
import json
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Set up the SQLAlchemy engine and Session
Base = declarative_base()

class EEGFileCatalog(Base):
    __tablename__ = 'eeg_file_catalog'

    id = Column(Integer, primary_key=True)
    status = Column(String)
    filename = Column(String)
    eegDataType = Column(String)
    jobType = Column(String)
    storagePath = Column(Text)
    ID = Column(String)
    email = Column(String)

def get_db_session():
    engine = create_engine('postgresql://airflow:airflow@localhost/airflow')
    Session = sessionmaker(bind=engine)
    return Session()

def catalog_eeg_files():
    folder_path = 'uploads/'  # Replace with the actual folder path
    info_files = glob.glob(os.path.join(folder_path, '*.info'))

    table_data = []
    for info_file in info_files:
        with open(info_file, 'r') as file:
            file_metadata = json.load(file)
            row = {
                'status': 'pending',
                'filename': file_metadata['MetaData'].get('filename', 'NA'),
                'eegDataType': file_metadata['MetaData'].get('eegDataType', 'NA'),
                'jobType': file_metadata['MetaData'].get('jobType', 'NA'),
                'storagePath': file_metadata['Storage'].get('Path', 'NA'),
                'ID': file_metadata.get('ID', 'NA'),
                'email': file_metadata['MetaData'].get('email', 'NA')
            }
            table_data.append(row)

    session = get_db_session()

    for row in table_data:
        eeg_file = EEGFileCatalog(**row)
        session.add(eeg_file)

    session.commit()
    session.close()

    # Display the table
    session = get_db_session()
    records = session.query(EEGFileCatalog).all()
    print("EEG File Catalog:")
    print("=" * 50)
    for record in records:
        print(f"ID: {record.ID}")
        print(f"Filename: {record.filename}")
        print(f"EEG Data Type: {record.eegDataType}")
        print(f"Job Type: {record.jobType}")
        print(f"Storage Path: {record.storagePath}")
        print(f"Email: {record.email}")
        print(f"Status: {record.status}")
        print("-" * 50)
    session.close()

    # Check for new files
    if len(info_files) > len(records):
        print("New file(s) detected!")

catalog_task = PythonOperator(
    task_id='catalog_eeg_files',
    python_callable=catalog_eeg_files,
    dag=dag,
)