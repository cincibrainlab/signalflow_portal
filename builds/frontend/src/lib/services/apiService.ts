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
      // console.log('Response headers:', response.headers);
      
      const data = await response.json();
      if (!response.ok) {
        console.log('Response data:', data);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return data;
  } catch (error) {
      console.error('Error fetching original file catalog:', error);
      throw error;
  }
}

export async function getMatchingFiles(valid_formats: any[], valid_paradigms: any[]) {
  try {
      const url = `${baseUrl}get-matching-files`;
      const response = await fetch(url, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ valid_formats, valid_paradigms })
      });

      console.log('Response status:', response.status);
      // console.log('Response headers:', response.headers);
      
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

export async function getFormats() {
  try {
      const response = await fetch(`${baseUrl}list-eeg-formats`);
      console.log('Response status:', response.status);
      // console.log('Response headers:', response.headers);
      
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Format Response data:', data);
      return data;
  } catch (error) {
      console.error('Error fetching eeg formats:', error);
      throw error;
  }
}

export async function getParadigms() {
  try {
      const response = await fetch(`${baseUrl}list-eeg-paradigms`);
      console.log('Response status:', response.status);
      // console.log('Response headers:', response.headers);
      
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Paradigm Response data:', data);
      return data;
  } catch (error) {
      console.error('Error fetching eeg paradigms:', error);
      throw error;
  }
}

export async function getAnalysisFunctions() {
  try {
      const response = await fetch(`${baseUrl}list-analysis-functions`);
      console.log('Response status:', response.status);
      // console.log('Response headers:', response.headers);
      
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Function Response data:', data);
      return data;
  } catch (error) {
      console.error('Error fetching eeg paradigms:', error);
      throw error;
  }
}

export async function getParticipants() {
  try {
      const response = await fetch(`${baseUrl}get-participants`);
      console.log('Get Participants Response status:', response.status);
      
      const data = await response.json();
      
      if (!response.ok) {
        console.log('Response data:', data);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return data;
  } catch (error) {
      console.error('Error fetching participants:', error);
      throw error;
  }
}

export async function getParticipant(participantObjectId: string) {
  try {
      const response = await fetch(`${baseUrl}get-participant/${participantObjectId}`);
      console.log('Get Participant Response status:', response.status);

      const data = await response.json();
      if (!response.ok) {
          console.log('Response data:', data);
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      let participantObject = data.participant;
      return participantObject;
  } catch (error) {
      console.error('Error fetching participant:', error);
      throw error;
  }
}

export async function getEEGFormat(FormatObjectID: string) {
  try { 
      const response = await fetch(`${baseUrl}get-eeg-format/${FormatObjectID}`);
      console.log('Get EEG Format Response status:', response.status);

      const data = await response.json();
      if (!response.ok) {
          console.log('Response data:', data);
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      let formatObject = data.eeg_format;
      return formatObject;
  } catch (error) {
      console.error('Error fetching EEG format:', error);
      throw error;
  }
}

export async function getParadigm(ParadigmObjectID: string) {
  try { 
      const response = await fetch(`${baseUrl}get-eeg-paradigm/${ParadigmObjectID}`);
      console.log('Get EEG Paradigm Response status:', response.status);

      const data = await response.json();
      if (!response.ok) {
          console.log('Response data:', data);
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      let paradigmObject = data.eeg_paradigm;
      return paradigmObject;
  } catch (error) {
      console.error('Error fetching EEG paradigm:', error);
      throw error;
  }
}

export async function assignParticipantToFile(ID: string, fileId: string) {
  console.log(`Assigning participant ${ID} to file ${fileId}`);
  const response = await fetch(`${baseUrl}assign-participant-to-file`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ ID, fileId })
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to assign participant to file');
  }

  return response.json();
}

export async function assignEEGFormatToFile(ID: string, fileId: string) {
  console.log(`Assigning EEG format ${ID} to file ${fileId}`);
  const response = await fetch(`${baseUrl}assign-eeg-format-to-file`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ ID, fileId })
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to assign EEG format to file');
  }

  return response.json();
}

export async function assignEEGParadigmToFile(ID: string, fileId: string) {
  console.log(`Assigning EEG paradigm ${ID} to file ${fileId}`);
  const response = await fetch(`${baseUrl}assign-eeg-paradigm-to-file`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ ID, fileId })
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to assign EEG paradigm to file');
  }

  return response.json();
}

export async function addParticipant(participantData: any) {
  console.log(JSON.stringify(participantData))
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

export async function addAnalysis(analysisData: any) {
  console.log(JSON.stringify(analysisData))
  const response = await fetch(`${baseUrl}add-analysis`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(analysisData),
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

export async function getFormOptions(form_name: string) {
  try {
      const response = await fetch(`${baseUrl}get-form-options/${form_name}`);
      console.log('Get Form Options Response status:', response.status);
      
      const data = await response.json();
      if (!response.ok) {
        console.log('Response data:', data);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return data;
  } catch (error) {
      console.error('Error fetching form options:', error);
      throw error;
  }
}