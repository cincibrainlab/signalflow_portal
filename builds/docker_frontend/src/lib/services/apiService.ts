// src/services/apiService.ts
import type { DatasetRow } from '../types';

const baseUrl = import.meta.env.VITE_API_BASE_URL;

export async function getEEGFormats() {
  const response = await fetch(`${baseUrl}list-eeg-formats`);
  return response.json();
}

export async function getEEGParadigms() {
  const response = await fetch(`${baseUrl}list-eeg-paradigms`);
  return response.json();
}

export async function getEmails() {
  const response = await fetch(`${baseUrl}list-emails`);
  return response.json();
}

export async function getUploadCatalog() {
  const response = await fetch(`${baseUrl}get-upload-catalog`);
  return response.json();
}

export async function getImportCatalog() {
  const response = await fetch(`${baseUrl}get-import-catalog`);
  return response.json();
}

export async function getDatasetCatalog() {
  const response = await fetch(`${baseUrl}get-dataset-catalog`);
  return response.json();
}

export async function getDatasetStats() {
  const response = await fetch(`${baseUrl}get-dataset-stats`);
  return response.json();
}

export async function processUploads() {
  const response = await fetch(`${baseUrl}process-uploads`);
  return response.json();
}

export async function addDataset(datasetEntry: DatasetRow) {
  console.log(`Adding dataset: ${JSON.stringify(datasetEntry)}`);
  const response = await fetch(`${baseUrl}add-dataset`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(datasetEntry)
  });
  return response.json();
}
export async function mergeDatasets(datasetId1: string, datasetId2: string) {
  console.log(`Merging datasets: ${datasetId1} and ${datasetId2}`);
  const response = await fetch(`${baseUrl}merge-datasets`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ dataset_id1: datasetId1, dataset_id2: datasetId2 })
  });
  return response.json();
}


export async function updateDataset(datasetEntry: DatasetRow) {
  console.log(`Updating dataset: ${JSON.stringify(datasetEntry)}`);
  const response = await fetch(`${baseUrl}update-dataset`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(datasetEntry)
  });
  console.log(`Response from update-dataset: ${JSON.stringify(response)}`);
  return response.json();
}


export async function callAPI(apiSuffix: string): Promise<string> {
    console.log(`Attempting to call API with suffix: ${apiSuffix}`);
    try {
        const response = await fetch(`${baseUrl}${apiSuffix}`);
        console.log(`API call successful: ${baseUrl}${apiSuffix}`);
        const data = await response.json();
        console.log(`Data received from API: ${JSON.stringify(data)}`);
        return JSON.stringify(data);
    } catch (error) {
        console.error(`Error during API call to ${apiSuffix}: ${error}`);
        return JSON.stringify({ error: `Failed to connect to ${apiSuffix} API.` });
    }
}