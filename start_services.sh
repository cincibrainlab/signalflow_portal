#!/bin/bash

export BACKEND_PORT=8001
export FRONTEND_PORT=5173
export DB_PORT=27017
export UPLOADER_PORT=1080

docker compose up --build 