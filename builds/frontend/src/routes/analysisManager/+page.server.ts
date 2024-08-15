import { getAnalyses, getParadigms, getFormats, getAnalysisFlows, getTags } from '$lib/services/apiService';
import type { PageServerLoad } from './$types';


export const load: PageServerLoad = async ({}) => {
    try {
        const [analyses, uniqueParadigms, uniqueFormats, uniqueFlows, tags] = await Promise.all([
            getAnalyses(),
            getParadigms(),
            getFormats(),
            getAnalysisFlows(),
            getTags()
        ]);
        return {
            analyses,
            uniqueParadigms,
            uniqueFormats,
            uniqueFlows,
            uniqueCategories: ["Connectivity", "Psd"],
            tags
        };
    } catch (error) {
        console.error('Error fetching data:', error);
        return {
            analyses: [],
            uniqueParadigms: ["All"],
            uniqueFormats: ["All"],
            uniqueFlows: [],
            uniqueCategories: ["Connectivity", "Psd"],
            tags: []
        };
    }
};