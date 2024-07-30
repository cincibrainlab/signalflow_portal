#!/bin/bash

# Start the mongo database in a new terminal
gnome-terminal -- bash -c "docker compose up -d sf_db sf_uploader; exec bash"

# Start the Python backend in a new terminal
gnome-terminal -- bash -c "cd builds/backend && python main.py; exec bash"

# Start the Svelte frontend in another new terminal
gnome-terminal -- bash -c "cd builds/frontend && npm run dev; exec bash"

# Start the Prefect server in another new terminal
gnome-terminal -- bash -c "prefect worker start --pool analysis-process-pool; exec bash"
