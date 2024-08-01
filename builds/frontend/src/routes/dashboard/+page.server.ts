import { fetchPrefectStats } from '$lib/services/prefectAPI';
import { getAnalysisFromDeploymentID, getAnalysisFlow, getMatchingFiles } from '$lib/services/apiService';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
    const deploymentId = url.searchParams.get('id');
    
    if (!deploymentId) {
        return { error: 'No deployment ID provided' };
    }

    try {
        const [prefectStats, analysis] = await Promise.all([
            fetchPrefectStats(deploymentId),
            getAnalysisFromDeploymentID(deploymentId)
        ]);

        const analysisFlow = await getAnalysisFlow(analysis.analysis_flow);
        const allFiles = await getMatchingFiles(analysis.valid_formats, analysis.valid_paradigms);

        const existingFileNames = new Set(prefectStats.runs.map(run => run.name));
        const possibleFiles = allFiles.filter(file => !existingFileNames.has(file.original_name));

        return {
            prefectStats,
            analysis,
            analysisFlow,
            possibleFiles,
            deploymentId
        };
    } catch (error) {
        console.error('Error fetching data:', error);
        return {
            error: 'Failed to fetch data',
            deploymentId
        };
    }
};