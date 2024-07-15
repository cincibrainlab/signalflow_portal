// src/services/apiService.ts
import type { DatasetRow } from '../types';

const baseUrl = "http://localhost:3005/api/";


export async function checkDbConnection() {
  console.log(`Base URL: ${baseUrl}`);
  const response = await fetch(`${baseUrl}check-db-connection`);
  const data = await response.json();
  console.log(`Data: data`);
  console.log(`Status: ${response.status}`);  
  return { status: response.status, data };
}

export async function processUploads() {
  const response = await fetch(`${baseUrl}process-uploads`);
  return response.json();
}

export async function getOriginalFileCatalog() {
  try {
      const response = await fetch(`${baseUrl}get-original-file-catalog`);
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Response data:', data);
      return data;
  } catch (error) {
      console.error('Error fetching original file catalog:', error);
      throw error;
  }
}

export async function getParticipants() {
  try {
      const response = await fetch(`${baseUrl}get-participants`);
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Response data:', data);
      return data;
  } catch (error) {
      console.error('Error fetching participants:', error);
      throw error;
  }
}

export async function getParticipant(participantObjectId: string) {
  try {
      const response = await fetch(`${baseUrl}get-participant/${participantObjectId}`);
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Response data:', data);
      let participantObject = data.participant;
      return participantObject;
  } catch (error) {
      console.error('Error fetching participant:', error);
      throw error;
  }
}

export async function assignParticipantToFile(participantId: string, fileId: string) {
  console.log(`Assigning participant ${participantId} to file ${fileId}`);
  const response = await fetch(`${baseUrl}assign-participant-to-file`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ participantId, fileId })
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to assign participant to file');
  }

  return response.json();
}

export async function addParticipant(participantData: any) {
  const response = await fetch(`${baseUrl}add-participant`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(participantData),
  });

  if (!response.ok) {
    throw new Error('Failed to add participant');
  }

  return await response.json();
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