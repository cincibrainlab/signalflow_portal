from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator  # Updated import statement
from airflow.sensors.base import BaseSensorOperator  # Updated import statement
from airflow.operators.python import PythonOperator  # Updated import statement
from airflow.models import Variable
import os
import json
import yaml

# Directory to monitor
UPLOADS_DIR = '/uploads'

# Default args
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

class CustomFileSensor(BaseSensorOperator):
    def __init__(self, directory, file_extension, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory = directory
        self.file_extension = file_extension

    def poke(self, context):
        files = os.listdir(self.directory)
        for file in files:
            if file.endswith(self.file_extension):
                context['ti'].xcom_push(key='detected_file', value=file)
                return True
        return False

def process_files(**kwargs):
    """
    Process the new .info file detected by CustomFileSensor.
    """
    ti = kwargs['ti']
    detected_file = ti.xcom_pull(key='detected_file', task_ids='wait_for_new_info_files')
    info_file_path = os.path.join(UPLOADS_DIR, detected_file)

    # Read JSON data from the .info file
    with open(info_file_path, 'r') as file:
        info_data = json.load(file)

    # Define the output YAML file name
    yaml_file_name = os.path.splitext(detected_file)[0] + '.yaml'
    yaml_file_path = os.path.join(UPLOADS_DIR, yaml_file_name)

    # Write data to the YAML file
    with open(yaml_file_path, 'w') as file:
        yaml.dump(info_data, file, default_flow_style=False)

    print(f"Processed {detected_file}: Created {yaml_file_name}")

with DAG('detect_new_files_on_condition', default_args=default_args, schedule_interval='* * * * *') as dag:  # Updated parameter
    start = EmptyOperator(task_id='start')  # Updated operator

    wait_for_files = CustomFileSensor(
        task_id='wait_for_new_info_files',
        directory=UPLOADS_DIR,
        file_extension='.info',
        timeout=600,  # Timeout in seconds after which the sensor gives up
        poke_interval=30  # Check every 30 seconds
    )

    process_files_task = PythonOperator(
        task_id='process_new_files',
        python_callable=process_files,
        provide_context=True
    )

    start >> wait_for_files >> process_files_task

