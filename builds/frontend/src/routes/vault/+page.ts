import { getOriginalFileCatalog, getParticipants, getParadigms, getFormats, getFormOptions, getEEGFormat, getParticipant, getParadigm } from '$lib/services/apiService';

/** @type {import('./$types').PageLoad} */
export async function load({ }) {
    try {
        const [fileCatalog, participants, paradigms, formats, diagnosisOptions, ageGroupOptions] = await Promise.all([
            getOriginalFileCatalog(),
            getParticipants(),
            getParadigms(),
            getFormats(),
            getFormOptions("Diagnosis"),
            getFormOptions("AgeGroup")
        ]);

        // Process files
        const setFiles = fileCatalog.filter((file: any) => file.is_set_file === true);
        const filesWithObjects = await getObjectsInFiles(setFiles);

        // Process other data
        const uniqueParadigms = ["All", ...paradigms.map((item: any) => item.name)];
        const uniqueFormats = formats.map((item: any) => item.name);
        const uniqueDiagnoses = ["All", ...diagnosisOptions.form_options];
        const uniqueAgeGroups = ["All", ...ageGroupOptions.form_options];

        return {
            files: filesWithObjects,
            participants,
            uniqueParadigms,
            uniqueFormats,
            uniqueDiagnoses,
            uniqueAgeGroups
        };
    } catch (error) {
        console.error('Error fetching data:', error);
        // Handle the error appropriately
        return {
            files: [],
            participants: [],
            uniqueParadigms: ["All"],
            uniqueFormats: [],
            uniqueDiagnoses: ["All"],
            uniqueAgeGroups: ["All"]
        };
    }
}

async function getObjectsInFiles(files: any[]) {
    const filesWithObjects = await Promise.all(
        files.map(async (file) => {
            if (file.eeg_format) {
                const formatData = await getEEGFormat(file.eeg_format);
                file = { ...file, formatData };
            }
            if (file.participant) {
                const participantData = await getParticipant(file.participant);
                file = { ...file, participantData };
            }
            if (file.eeg_paradigm) {
                const paradigmData = await getParadigm(file.eeg_paradigm);
                file = { ...file, paradigmData };
            }
            return file;
        })
    );
    return filesWithObjects;
}