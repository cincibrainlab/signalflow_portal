#Installation
## Downloading the Repository 

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

   *Docker images may take some time to build

3. **Access the Application**:
   Open your web browser and go to `http://localhost:5173` to access the SignalflowEEG application.
