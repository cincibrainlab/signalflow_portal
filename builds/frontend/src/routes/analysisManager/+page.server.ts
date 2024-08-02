import { getAnalyses, getParadigms, getFormats, getAnalysisFlows } from '$lib/services/apiService';
import type { PageServerLoad } from './$types';


export const load: PageServerLoad = async ({}) => {
    try {
        const [analyses, uniqueParadigms, uniqueFormats, uniqueFlows] = await Promise.all([
            getAnalyses(),
            getParadigms(),
            getFormats(),
            getAnalysisFlows()
        ]);

        return {
            analyses,
            uniqueParadigms,
            uniqueFormats,
            uniqueFlows,
            uniqueCategories: ["Connectivity", "test", "test2"]
        };
    } catch (error) {
        console.error('Error fetching data:', error);
        return {
            analyses: [],
            uniqueParadigms: ["All"],
            uniqueFormats: ["All"],
            uniqueFlows: [],
            uniqueCategories: ["Connectivity", "test", "test2"]
        };
    }
};