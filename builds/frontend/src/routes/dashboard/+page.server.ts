import { fetchPrefectStats } from '$lib/services/prefectAPI';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
    const deploymentId = url.searchParams.get('id');
    
    if (!deploymentId) {
        return {
            prefectStats: null,
            error: 'No deployment ID provided'
        };
    }

    try {
        const prefectStats = await fetchPrefectStats(deploymentId);
        return {
            prefectStats,
            deploymentId
        };
    } catch (error) {
        console.error('Error fetching Prefect stats:', error);
        return {
            prefectStats: null,
            error: 'Failed to fetch Prefect stats',
            deploymentId
        };
    }
};
