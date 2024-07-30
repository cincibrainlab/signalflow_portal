import { getAnalyses, getParadigms, getFormats, getAnalysisFunctions } from '$lib/services/apiService';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({}) => {
    try {
        const [analyses, paradigms, formats, functions] = await Promise.all([
            getAnalyses(),
            getParadigms(),
            getFormats(),
            getAnalysisFunctions()
        ]);

        return {
            analyses,
            uniqueParadigms: ["All", ...paradigms.map((item: { name: any; }) => item.name)],
            uniqueFormats: ["All", ...formats.map((item: { name: any; }) => item.name)],
            uniqueFunctions: functions,
            uniqueCategories: ["Connectivity", "test", "test2"]
        };
    } catch (error) {
        console.error('Error fetching data:', error);
        return {
            analyses: [],
            uniqueParadigms: ["All"],
            uniqueFormats: ["All"],
            uniqueFunctions: [],
            uniqueCategories: ["Connectivity", "test", "test2"]
        };
    }
};