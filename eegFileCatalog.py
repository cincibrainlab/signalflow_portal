import os
import glob
import json
#import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from tabulate import tabulate
import pandas as pd

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
    ID = Column(String, unique=True)
    email = Column(String)

def get_db_session():
    engine = create_engine('postgresql://airflow:airflow@localhost/airflow')
    Base.metadata.create_all(engine)  # This line creates all tables
    Session = sessionmaker(bind=engine)
    return Session()

def catalog_eeg_files():
    current_directory = os.getcwd()
    print("Current Directory:", current_directory)
    folder_path = '/home/ernie/github/signalflow_portal/uploads'  # Replace with the actual folder path
    info_files = glob.glob(os.path.join(folder_path, '*.info'))
    print(info_files)
    session = get_db_session()

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

            # Check if the record already exists in the database
            existing_record = session.query(EEGFileCatalog).filter(EEGFileCatalog.ID == row['ID']).first()
            if existing_record:
                # Update the existing record
                existing_record.status = row['status']
                existing_record.filename = row['filename']
                existing_record.eegDataType = row['eegDataType']
                existing_record.jobType = row['jobType']
                existing_record.storagePath = row['storagePath']
                existing_record.email = row['email']
            else:
                # Create a new record
                eeg_file = EEGFileCatalog(**row)
                session.add(eeg_file)

    session.commit()
    session.close()

    # Check for new files
    if len(info_files) > len(session.query(EEGFileCatalog).all()):
        print("New file(s) detected!")
        
def query_set_files():
    session = get_db_session()
    set_files = session.query(EEGFileCatalog).filter(EEGFileCatalog.filename.ilike('%set%')).all()
    session.close()
    return set_files

def update_row(row):
    session = get_db_session()
    filename = row['filename']
    fdt_filename = filename.replace('.set', '.fdt')
    fdt_file = session.query(EEGFileCatalog).filter(EEGFileCatalog.filename == fdt_filename).first()
    if fdt_file:
        row['fdtFileName'] = fdt_filename
        row['hasFDTFile'] = True
        row['fdtFilePath'] = fdt_file.storagePath
    else:
        row['fdtFileName'] = fdt_filename
        row['hasFDTFile'] = False
        row['fdtFilePath'] = 'NA'
    session.close()
    return row

def update_table_with_fdt_files(df):
    return df.apply(update_row, axis=1)

if __name__ == "__main__":
    catalog_eeg_files()
    set_files = query_set_files()
    table_data = []
    for file in set_files:
        table_data.append([file.ID, file.filename, file.eegDataType, file.jobType, file.storagePath, file.email, file.status])
    df = pd.DataFrame(table_data, columns=["id", "filename", "eegDataType", "jobType", "storagePath", "email", "status"])
    print(df)
    
    updated_table_data = update_table_with_fdt_files(df)
    print(tabulate(updated_table_data, headers='keys', tablefmt='psql'))
