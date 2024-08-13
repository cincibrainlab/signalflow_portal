@echo off

:: Set environment variables
wsl export BACKEND_PORT=8001
wsl export FRONTEND_PORT=5173
wsl export DB_PORT=27017
wsl export UPLOADER_PORT=1080

:: Start all services using Docker Compose
wsl docker compose up --build 