import type { PageServerLoad } from './$types';


export const load: PageServerLoad = async ({ url }) => {
    const upload_id = url.searchParams.get('id');


    
    if (!upload_id) {
        return {
            upload_id: null,
            error: 'No upload ID provided'
        };
    }
    else {
        return {
            upload_id: upload_id
        };
    }
};
