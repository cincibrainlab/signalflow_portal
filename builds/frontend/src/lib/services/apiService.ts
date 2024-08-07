// src/services/apiService.ts
import pako from 'pako';


export const baseUrl = "http://127.0.0.1:3005/api/";

const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

async function cachedFetch(url: string, options?: RequestInit) {
  const cacheKey = `${url}${options ? JSON.stringify(options) : ''}`;
  const cached = cache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }

  const response = await fetch(url, options);
  const data = await response.json();

  if (response.ok) {
    cache.set(cacheKey, { data, timestamp: Date.now() });
  }

  return data;
}

export async function checkDbConnection() {
  console.log(`Base URL: ${baseUrl}`);
  const response = await fetch(`${baseUrl}check-db-connection`);
  const data = await response.json();
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
      console.log(data)
      return data;
  } catch (error) {
      console.error('Error fetching original file catalog:', error);
      throw error;
  }
}

export async function getOriginalFileFromUploadID(OriginalImportFile_Uploadid: string) {
  try {
      const response = await fetch(`${baseUrl}get-original-file-from-upload-id/${OriginalImportFile_Uploadid}`);
      console.log('Get Original File Response status:', response.status);

      const data = await response.json();
      if (!response.ok) {
          console.log('Response data:', data);
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      let analysisObject = data;
      return analysisObject;
  } catch (error) {
      console.error('Error fetching analysis:', error);
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

export async function assignFileToAnalysis(analysisId: string, OriginalImportFile_id: string) {
  try {
      const url = `${baseUrl}assign-file-to-analysis`;
      const response = await fetch(url, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ analysisId, OriginalImportFile_id })
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
      console.error('Error assinging file to analysis:', error);
      throw error;
  }
}


export async function getFormats() {
  try {
    const data = await cachedFetch(`${baseUrl}list-eeg-formats`);
    console.log('Response status: OK (cached or fresh)');
    return data;
  } catch (error) {
    console.error('Error fetching eeg formats:', error);
    throw error;
  }
}

export async function getParadigms() {
  try {
    const data = await cachedFetch(`${baseUrl}list-eeg-paradigms`);
    console.log('Response status: OK (cached or fresh)');
    return data;
  } catch (error) {
    console.error('Error fetching eeg paradigms:', error);
    throw error;
  }
}

export async function getAnalysisFlows() {
    try {
        const data = await cachedFetch(`${baseUrl}list-analysis-flows`);
        console.log('Get Analysis Flows Response status: OK (cached or fresh)');
        return data;
    } catch (error) {
        console.error('Error fetching analysis flows:', error);
        throw error;
    }
}

export async function getAnalysisFlow(id: string) {
    try {
        const data = await cachedFetch(`${baseUrl}get-analysis-flow/${id}`);
        console.log('Get Analysis Flow Response status: OK (cached or fresh)');
        return data;
    } catch (error) {
        console.error('Error fetching analysis flow:', error);
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
    const data = await cachedFetch(`${baseUrl}get-participant/${participantObjectId}`);
    console.log('Get Participant Response status: OK (cached or fresh)');
    return data.participant;
  } catch (error) {
    console.error('Error fetching participant:', error);
    throw error;
  }
}

export async function getAnalysisFromDeploymentID(DeploymentID: string) {
  try {
      const response = await fetch(`${baseUrl}get-analysis-from-deployment-id/${DeploymentID}`);
      console.log('Get Analysis Response status:', response.status);

      const data = await response.json();
      if (!response.ok) {
          console.log('Response data:', data);
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      let analysisObject = data;
      return analysisObject;
  } catch (error) {
      console.error('Error fetching analysis:', error);
      throw error;
  }
}

export async function getEEGFormat(FormatObjectID: string) {
  try { 
    const data = await cachedFetch(`${baseUrl}get-eeg-format/${FormatObjectID}`);
    console.log('Get EEG Format Response status: OK (cached or fresh)');
    return data.eeg_format;
  } catch (error) {
    console.error('Error fetching EEG format:', error);
    throw error;
  }
}

export async function getParadigm(ParadigmObjectID: string) {
  try { 
    const data = await cachedFetch(`${baseUrl}get-eeg-paradigm/${ParadigmObjectID}`);
    console.log('Get EEG Paradigm Response status: OK (cached or fresh)');
    return data.eeg_paradigm;
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

  cache.delete(`${baseUrl}get-original-file-catalog`);
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

  cache.delete(`${baseUrl}get-original-file-catalog`);
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

  cache.delete(`${baseUrl}get-original-file-catalog`);
  return response.json();
}

export async function assignTagsToFile(tags: string[], fileId: string) {
  try {
    const url = `${baseUrl}assign-tags-to-file/${fileId}`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify( tags )
    });
    
    const responseData = await response.json();
    console.log('Response data:', responseData);

    if (!response.ok) {
      throw new Error(`Failed to assign tags: ${JSON.stringify(responseData)}`);
    }
    cache.delete(`${baseUrl}get-tags/${fileId}`);
    return responseData;
  } catch (error) {
    console.error('Error in assignTagsToFile:', error);
    throw error;
  }
}

export async function getTags(fileId: string) {
  const data = await cachedFetch(`${baseUrl}get-tags/${fileId}`);
  if (!data.ok) {
    throw new Error('Failed to get tags');
  }
  console.log('Get Tags Response status: OK (cached or fresh)');
  return data;
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

  // Invalidate the cache for participants
  cache.delete(`${baseUrl}get-participants`);

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
    const data = await cachedFetch(`${baseUrl}get-form-options/${form_name}`);
    console.log('Get Form Options Response status: OK (cached or fresh)');
    return data;
  } catch (error) {
    console.error('Error fetching form options:', error);
    throw error;
  }
}


export async function getAnalyses() {
  try {
    const response = await fetch(`${baseUrl}get-analyses`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log('Get Analyses Response status: OK (cached or fresh)');
    return data;
  } catch (error) {
    console.error('Error fetching analyses:', error);
    throw error;
  }
}

export async function addAnalysis(analysisData: any) {
  const response = await fetch(`${baseUrl}add-analysis`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(analysisData),
  });

  if (!response.ok) {
    throw new Error('Failed to add analysis');
  }

  return await response.json();
}

export async function getFileRuns(upload_id: string) {
  try {
    const response = await fetch(`${baseUrl}get-file-runs/${upload_id}`);
    console.log('Get File Runs Response status:', response.status);

    const data = await response.json();
    if (!response.ok) {
      console.log('Response data:', data);
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching file runs:', error);
    throw error;
  }
}

export async function getFileRun(file_run_id: string) {
  try {
    const response = await fetch(`${baseUrl}get-file-run/${file_run_id}`);
    console.log('Get File Run Response status:', response.status);

    const data = await response.json();
    if (!response.ok) {
      console.log('Response data:', data);
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching file run:', error);
    throw error;
  }
}

export async function sendContactMessage(formData: any) {
  console.log(JSON.stringify(formData))
  const response = await fetch(`${baseUrl}sendContactMessage`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formData),
  });

  if (!response.ok) {
    throw new Error('Failed to send contact message');
  }

  return await response.json();

}

export async function getEEGData(upload_id: string, sample_rate: number): Promise<any> {
  console.log(`Getting EEG data for upload ID: ${upload_id}`);
  try {
    const shapeResponse = await fetch(`${baseUrl}get-eeg-data-shape/${upload_id}`);
    console.log('Get EEG Data Shape Response status:', shapeResponse.status);
    const shapeData = await shapeResponse.json();
    console.log('Shape data:', shapeData);

    let numchannels = shapeData.shape[0];
    let samplingrate = sample_rate
    let OriginalSamplingRate = shapeData.sfreq

    console.log('Num channels:', numchannels);
    const response = await fetch(`${baseUrl}get-eeg-data/${upload_id}/${sample_rate}`);
    console.log('Get EEG Data Response status:', response.status);
    console.log('All response headers:', Object.fromEntries(response.headers));
    
    // Get the header
    const psdPath = response.headers.get('X-Psd-Path');
    console.log('PSD Path from header:', psdPath);
    
    const arrayBuffer = await response.arrayBuffer();

    // Decompress
    const decompressed = pako.inflate(new Uint8Array(arrayBuffer));
    // Parse NumPy array
    let array = parseNumpyArray(decompressed);
    // Now 'array' is a Float64Array
    console.log(array.length, array.constructor.name);
    // Reshape the array
    const reshapedArray = reshapeArray(array, numchannels);
    
    return {
      "num_channels": numchannels,
      "sampling_rate": samplingrate,
      "original_sampling_rate": OriginalSamplingRate,
      "data": reshapedArray,
      "psd_path": psdPath
    }
  } catch (error) {
    console.error('Error:', error);
    throw error; // Re-throw the error to be handled by the caller
  }
}

// Helper function to parse NumPy array (simplified for float64)
function parseNumpyArray(buffer: any): Float64Array {
  // Skip header (assuming .npy format, you may need to adjust this)
  const headerLength = new DataView(buffer.buffer).getUint16(8, true) + 10;
  const data = new Float64Array(buffer.buffer, headerLength);
  return data;
}

// Make sure this function is defined correctly
function reshapeArray(flatArray: Float64Array, rows: number): Float64Array[] {
  const cols = flatArray.length / rows;
  const result: Float64Array[] = [];
  
  for (let i = 0; i < rows; i++) {
    result.push(flatArray.subarray(i * cols, (i + 1) * cols));
  }
  
  return result;
}

export async function downloadFile(upload_id: any) {
  console.log(`Downloading EEG File for upload ID: ${upload_id}`);
  try {
    const response = await fetch(`${baseUrl}download-eeg-file/${upload_id}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'downloaded_files.zip';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Download failed:', error);
  }

}

export async function deleteTemporaryFile(fileName: string) {
  try {
      const response = await fetch(`${baseUrl}delete-temp-file/${fileName}`, {
          method: 'DELETE',
      });
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
  } catch (error) {
      console.error('Error deleting temporary file:', error);
      throw error;
  }
}

export async function getFileRunOutputFiles(fileRunId: string) {
  try {
      const response = await fetch(`${baseUrl}get-file-run-output-files/${fileRunId}`);
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
  } catch (error) {
      console.error('Error fetching file run output files:', error);
      throw error;
  }
}