<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import AnalysisDashboard from '$lib/components/AnalysisDashboard.svelte';

    const deploymentId = $page.params.id;

    function goBack() {
        goto('/runmanager');
    }
</script>

<div class="p-4">
    <button on:click={goBack} class="mb-4 bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
        Back to Analysis Manager
    </button>
    <AnalysisDashboard {deploymentId} />
</div>