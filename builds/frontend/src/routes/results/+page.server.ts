import type { PageServerLoad } from './$types'; // Import the 'FileType' type
import { getFileRun, getFileRunOutputFiles } from '$lib/services/apiService';

export const load: PageServerLoad = async ({ url }) => {
    const fileRunId = url.searchParams.get('id');
    if (!fileRunId) {
        throw new Error('File run ID is required');
    }
    return {
        fileRunId,
        fileRun: await getFileRun(fileRunId),
        outputFiles: await getFileRunOutputFiles(fileRunId)
    }
}