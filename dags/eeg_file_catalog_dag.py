from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from db import drop_all_tables
from portal_utils import load_config
from upload_catalog import update_upload_catalog
from import_catalog import update_import_catalog
import os
import glob
import logging

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
    description='Process new EEG file uploads and update catalogs',
    schedule_interval=timedelta(days=1),
)

def find_info_files(upload_dir):
    info_files = glob.glob(os.path.join(upload_dir, "*.info"))
    logging.info(f"Detected {len(info_files)} .info files in {upload_dir}.")
    return info_files

def process_new_uploads(upload_dir, **context):
    logging.info(f"Scanning upload directory: {upload_dir}")
    update_upload_catalog(find_info_files(upload_dir))
    update_import_catalog()
    logging.info("Upload and import catalogs updated.")

drop_all_tables_task = PythonOperator(
    task_id='drop_all_tables',
    python_callable=drop_all_tables,
    dag=dag,
)

process_new_uploads_task = PythonOperator(
    task_id='process_new_uploads',
    python_callable=process_new_uploads,
    op_kwargs={'upload_dir': load_config()['folder_paths']['uploads']},
    dag=dag,
)

drop_all_tables_task >> process_new_uploads_task