@echo off

:: Set environment variables
set BACKEND_PORT=8001
set FRONTEND_PORT=5173
set DB_PORT=27017
set UPLOADER_PORT=1080

:: Start all services using Docker Compose
docker compose up --build sf_portal