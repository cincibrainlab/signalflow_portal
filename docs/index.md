# SignalFlow Vault 

Welcome to the SignalflowEEG documentation. This guide will help you understand how to set up and use the SignalflowEEG application, which includes both a frontend (JavaScript) and a backend (Python/FastAPI).

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [API Reference](#api-reference)
6. [Frontend Guide](#frontend-guide)
7. [Backend Guide](#backend-guide)
8. [EEG Data Processing](#eeg-data-processing)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)
11. [Contributing](#contributing)
12. [License](#license)

## Introduction

SignalflowEEG is an application designed for processing EEG data. It features a robust backend built with Python and FastAPI, and a dynamic frontend developed using JavaScript.

### Prerequisites

- Python 3.8+
- Node.js 18+
- Docker (optional, for containerized deployment)

## Installation

### Downloading the Repository 

To get started with editing the files, you need to clone the repository to your local machine. Follow these steps:

1. **Clone the Repository**:
   Open your terminal and run the following command to clone the repository:
   ```bash
   git clone https://github.com/cincibrainlab/SignalflowEEG.git
   ```
2. **Navigate to the Project Directory**:
   Change into the project directory:
   ```bash
   cd SignalflowEEG
   ```

3. **Build and Execute Docker Images**
   In order to run the vault you will need 3 docker containers running, all of which are defined in the docker-compose.yaml
   In order to create these containers you can run:
   ```bash
   docker compose up -d sf_uploader sf_db sf_portal
   ```

   It may take some time for the images to build but once they are running you will have a completely containerized application!


### Other backend components

### Docker Configuration for sf_uploader

The `sf_uploader` service is defined in the `docker-compose.yaml` file. This service uses the `tusproject/tusd:v1.9` image to handle file uploads. Below are the key configurations for this service:

- **Container Name**: `sf_uploader`
- **Image**: `tusproject/tusd:v1.9`
- **Command**: `-verbose -upload-dir=/uploads`
- **Volumes**:
  - `tusd:/data`
  - `./portal_files/uploads:/uploads`
  - `./portal_files/input:/input`
  - `./portal_files/info_archive:/info_archive`
  - `./portal_files/output:/output`
- **Ports**: `3001:1080`
- **Restart Policy**: `always`
- **Networks**: `eeg-network`

This configuration ensures that the `sf_uploader` service is always running and accessible on port `3001`. The volumes map local directories to the container's directories, facilitating data persistence and access across different services.


### Database Configuration for sf_db

The `sf_db` service is defined in the `docker-compose.yaml` file. This service uses the `postgres:13` image to handle database operations. Below are the key configurations for this service:

- **Container Name**: `sf_db`
- **Image**: `postgres:13`
- **Ports**: `3002:5432`
- **Environment Variables**:
  - `POSTGRES_USER`: `sfportal`
  - `POSTGRES_PASSWORD`: `sfportal`
  - `POSTGRES_DB`: `sfportal`
- **Volumes**:
  - `sfdb-db-volume:/var/lib/postgresql/data`
- **Restart Policy**: `always`
- **Networks**: `eeg-network`

This configuration ensures that the `sf_db` service is always running and accessible on port `3002`. The environment variables set up the database user, password, and database name. The volume maps a local directory to the container's directory, ensuring data persistence.


## Installation

### Downloading the Repository 

To get started with editing the files, you need to clone the repository to your local machine. Follow these steps:

1. **Clone the Repository**:
   Open your terminal and run the following command to clone the repository:
   ```bash
   git clone https://github.com/cincibrainlab/SignalflowEEG.git
   ```
2. **Navigate to the Project Directory**:
   Change into the project directory:
   ```bash
   cd SignalflowEEG
   ```

   And thats it!

3. **Build and Execute Docker Images**
   In order to run the vault you will need 3 docker containers running, all of which are defined in the docker-compose.yaml
   In order to create these containers you can run:
   ```bash
   docker compose up -d sf_uploader sf_db sf_portal
   ```

   It may take some time for the images to build but once they are running you will have a completely containerized application!
<!-- 3. **Install Dependencies**:
   Install the necessary dependencies for both the backend and frontend.

   **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

   **Frontend**:
   ```bash
   cd ../frontend
   npm install -->
   ```

4. **Start Application**

   **Start Docker Containers**:
   docker compose up sf_db sf_uploader -d

   **Backend**:
   ```bash
   cd backend
   ./start_fastapi.sh
   ```

   **Frontend**:
   ```bash
   cd ../frontend
   ./start_frontend.sh
   ```


### Using Docker for Production Deployment

For a production deployment, you can use Docker to containerize the application. Follow these steps:

1. **Build the Docker Images**:
   Navigate to the root directory of the project and run the following command to build the Docker image:
   ```bash
   docker compose up -d sf_uploader sf_db sf_portal
   ```

<!-- 2. **Run the Docker Container**:
   After building the image, you can run the container using:
   ```bash
   docker run -d -p 8000:8000 signalfloweeg:latest
   ``` -->

3. **Access the Application**:
   Open your web browser and go to `http://localhost:5173` to access the SignalflowEEG application.

4. **Stopping the Container**:
   To stop the running container, first find the container ID using:
   ```bash
   docker ps
   ```
   Then stop the container using:
   ```bash
   docker stop <container_id>
   ```

By following these instructions, you can easily set up your development environment and deploy the SignalflowEEG application using Docker for production.




### Backend Installation
