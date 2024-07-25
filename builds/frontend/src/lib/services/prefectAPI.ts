export const baseUrl = "http://localhost:3005/prefect/";

export interface PrefectStats {
    failed_runs: number;
    pending_runs: number;
    completed_runs: number;
    avg_runtime: string;
    completion_rate: number;
    total_runs: number;
    success_rate: number;
}

export async function fetchPrefectStats(): Promise<PrefectStats> {
    try {
        const response = await fetch(`${baseUrl}prefect-stats`);
        const rawText = await response.text();
        console.log("Raw response:", rawText);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = JSON.parse(rawText);
        return data;
    } catch (error) {
        console.error('Error fetching Prefect stats:', error);
        throw error;
    }
}

export async function createAnalysis(analysis_id: string, analysis_func: string) {
    try {
        const response = await fetch(`${baseUrl}run-analysis/${analysis_id}`);
        console.log('Run Analysis Response status:', response.status);
        
        const data = await response.json();
        if (!response.ok) {
          console.log('Response data:', data);
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return data;
    } catch (error) {
        console.error('Error running analysis:', error);
        throw error;
    }
  }