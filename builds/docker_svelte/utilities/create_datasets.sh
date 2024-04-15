BASE_URL="http://localhost:8001"

curl -X GET "$BASE_URL/api/clear-table/DatasetCatalog"

curl -X POST "$BASE_URL/api/add-dataset" \
    -H "Content-Type: application/json" \
    -d '{
        "dataset_name": "Resting State Analysis 2024",
        "description": "EEG data recorded in a resting state condition from 30 participants aged 20-40, aimed to study baseline brain activity.",
        "eeg_format_id": 1,
        "eeg_paradigm_id": 1
    }'

curl -X POST "$BASE_URL/api/add-dataset" \
    -H "Content-Type: application/json" \
    -d '{
        "dataset_name": "Visual Stimulus Response 2024",
        "description": "Data from an EEG study analyzing brain responses to visual stimuli, involving 50 subjects with stimuli displayed at varying intervals.",
        "eeg_format_id": 2,
        "eeg_paradigm_id": 3
    }'

curl -X POST "$BASE_URL/api/add-dataset" \
    -H "Content-Type: application/json" \
    -d '{
        "dataset_name": "Cognitive Task Performance 2024",
        "description": "EEG recordings from a cognitive task designed to elicit responses related to memory and attention in 40 elderly subjects.",
        "eeg_format_id": 3,
        "eeg_paradigm_id": 2
    }'
