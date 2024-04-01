from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import glob
import csv
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'eeg_file_catalog',
    default_args=default_args,
    description='Catalog EEG files and metadata',
    schedule=timedelta(minutes=5),
)

def catalog_eeg_files():
    folder_path = '/uploads'  # Replace with the actual folder path
    info_files = glob.glob(os.path.join(folder_path, '*.info'))
    
    table_data = []
    for info_file in info_files:
        with open(info_file, 'r') as file:
            file_metadata = json.load(file)
            
            metadata = file_metadata.get('MetaData', {})
            file_metadata['filename'] = metadata.get('filename', 'N/A')
            file_metadata['filetype'] = metadata.get('filetype', 'N/A')
            file_metadata['name'] = metadata.get('name', 'N/A')
            file_metadata['relativePath'] = metadata.get('relativePath', 'N/A')
            file_metadata['type'] = metadata.get('type', 'N/A')
            file_metadata['status'] = 'pending'
            
            table_data.append(file_metadata)
    
    # Save the table as a CSV file
    csv_file = '/uploads/catalog.csv'  # Replace with the desired file path
    with open(csv_file, 'w', newline='') as file:
        fieldnames = ['filename', 'filetype', 'name', 'relativePath', 'type', 'status']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(table_data)
    
    # Display the table
    print("EEG File Catalog:")
    print("=" * 50)
    for row in table_data:
        print(f"Filename: {row.get('filename', 'N/A')}")
        print(f"Filetype: {row.get('filetype', 'N/A')}")
        print(f"Name: {row.get('name', 'N/A')}")
        print(f"Relative Path: {row.get('relativePath', 'N/A')}")
        print(f"Type: {row.get('type', 'N/A')}")
        print(f"Status: {row.get('status', 'N/A')}")
        print("-" * 50)
    
    # Check for new files
    if len(info_files) > len(table_data):
        print("New file(s) detected!")

catalog_task = PythonOperator(
    task_id='catalog_eeg_files',
    python_callable=catalog_eeg_files,
    dag=dag,
)