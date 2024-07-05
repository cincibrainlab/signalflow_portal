<script>
    import EEGStudyVisualizer from '$lib/components/EEGStudyVisualizer.svelte'

    export let data
</script>

<EEGStudyVisualizer studyData={data.studyData} />