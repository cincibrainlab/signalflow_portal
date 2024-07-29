@echo off

:: Start the Postgres database in a new terminal
start cmd /k "docker compose up sf_db sf_uploader -d && cd builds/backend && python main.py"

:: Start the Svelte frontend in another new terminal
start cmd /k "cd builds/frontend && npm run dev"

:: Start the Prefect server in another new terminal
start cmd /k "prefect worker start --pool analysis-process-pool"


