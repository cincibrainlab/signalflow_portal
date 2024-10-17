#Docker
## Docker Usage
Docker can be managed using either the command line or the docker desktop application.
Some useful commands are: 

#### 1. Check Docker Version
To check the installed version of Docker, use:
   ```bash
   docker --version
   ```

#### 2. List Running Containers
To see all currently running containers:
   ```bash
   docker ps
   ```

#### 3. List All Containers
To list all containers, including stopped ones:
   ```bash
   docker ps -a
   ```

#### 4. Stop a Running Container
To stop a running container:
   ```bash
   docker stop <container_name_or_id>
   ```

#### 5. Start a Container
To start a stopped container:
   ```bash
   docker start <container_name_or_id>
   ```

#### 6. View Container Logs
To view the logs of a running container:
   ```bash
   docker logs <container_name_or_id>
   ```

## Configuration for sf_uploader

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


## Database Configuration for sf_db

The `sf_db` service is defined in the `docker-compose.yaml` file. This service uses the `postgres:13` image to handle database operations. Below are the key configurations for this service:

- **Container Name**: `sf_db`
- **Image**: `mongo:latest`
- **Ports**: `3002:27017`
- **Volumes**: `sfdb-db-volume:/data/db`
- **Restart Policy**: `always`
- **Networks**: `eeg-network`

This configuration ensures that the `sf_db` service is always running and accessible on port `3002`. The volume maps a local directory to the container's directory, ensuring data persistence.