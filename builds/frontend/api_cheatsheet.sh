curl http://localhost:3005/api/get-upload-catalog
curl http://localhost:3005/api/get-import-catalog
curl http://localhost:3005/api/load-database-summary
curl http://localhost:3005/api/get-portal-paths
curl http://localhost:3005/api/list-eeg-formats
curl http://localhost:3005/api/list-eeg-paradigms
curl http://localhost:3005/api/list-emails
curl http://localhost:3005/api/get-dataset-catalog
curl http://localhost:3005/api/process-uploads
curl http://localhost:3005/api/show_upload_catalog
curl http://localhost:3005/api/get-dataset-stats
curl http://localhost:3005/api/delete-database


curl -X POST http://localhost:3005/api/merge-datasets -H "Content-Type: application/json" -d '{"dataset_id1": "ed591e8b-a212-458a-9608-d4bfeee21a6b|#bc9bb", "dataset_id2": "dce9fe9d-601b-4f9c-881d-8f4b0b78ded9|#d470db"}'


