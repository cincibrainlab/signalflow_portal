export const baseUrl = `http://127.0.0.1:${import.meta.env.VITE_BACKEND_PORT || '3005'}/prefect/`;
export interface PrefectRun {
    id: string;
    name: string;
    status: string;
}

export interface PrefectStats {
    failed_runs: number;
    pending_runs: number;
    completed_runs: number;
    avg_runtime: string;
    completion_rate: number;
    total_runs: number;
    success_rate: number;
    runs: PrefectRun[];
}

export async function fetchPrefectStats(deploymentId: string): Promise<PrefectStats> {
    try {
        const response = await fetch(`${baseUrl}prefect-stats/${deploymentId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching Prefect stats:', error);
        throw error;
    }
}
