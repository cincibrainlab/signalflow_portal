# SignalFlow Portal

## Overview
The `signalflow_portal` is a comprehensive platform designed to streamline the execution of EEG analyses. Leveraging the power of Airflow, this system provides a robust and scalable infrastructure for orchestrating complex workflows, ensuring efficient and reliable data processing. The platform features a user-friendly web interface, a Python and MATLAB backend for analysis tasks, and an integrated uploader for seamless data ingestion.

## Key Features

<div class="feature">
  <h3>Airflow-based Job Scheduling</h3>
  <p>The platform utilizes Apache Airflow to orchestrate and automate the execution of EEG analysis tasks, ensuring reliable, scalable, and fault-tolerant job scheduling.</p>
</div>

<div class="feature">
  <h3>Web Interface</h3>
  <p>The system offers a user-friendly web interface, allowing researchers and analysts to easily manage their EEG analysis workflows, monitor job status, and access analysis results.</p>
</div>

<div class="feature">
  <h3>Python and MATLAB Backend</h3>
  <p>The platform supports both Python and MATLAB-based analysis tasks, providing flexibility and enabling the integration of a wide range of analytical tools and libraries.</p>
</div>

<div class="feature">
  <h3>Data Uploader</h3>
  <p>The integrated uploader facilitates the seamless ingestion of EEG data, ensuring a streamlined data management process.</p>
</div>

## Example Use Case
As a researcher, you can use the `signalflow_portal` to streamline your EEG analysis workflow. Simply upload your EEG data files to the platform, select the desired analysis (e.g., connectivity analysis), and the system will automatically process the data and email you the results, which will also be saved to a cloud drive for easy access.

## Getting Started
To get started with the `signalflow_portal`, please refer to the detailed installation and configuration instructions provided in the project's documentation.

## Contributing
We welcome contributions from the community to enhance the functionality and capabilities of the `signalflow_portal`. If you're interested in contributing, please review the project's guidelines and submit your proposals or pull requests.

## To install the project locally

## You NEED Python 3.10
```bash
docker compose up sf_db sf_uploader

cd builds/frontend
npm install

cd builds/backend
pip install -r requirements.txt

cd github
git clone https://github.com/cincibrainlab/signalfloweeg_py
cd signalfloweeg_py
pip install -e .

prefect cloud login
prefect work-pool create analysis-process-pool --type process
```

## To run
```bash
# For Windows
.\start_services.bat

# For Linux
./start_services.sh

```

