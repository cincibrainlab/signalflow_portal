<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import AnalysisDashboard from '$lib/components/AnalysisDashboard.svelte';

    $: deploymentId = $page.url.searchParams.get('id');

    function goBack() {
        goto('/analysisManager');
    }
</script>

<div class="p-4">
    <button on:click={goBack} class="mb-4 bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
        Back to Analysis Manager
    </button>
    {#if deploymentId}
        <AnalysisDashboard {deploymentId} />
    {:else}
        <p>No deployment ID provided.</p>
    {/if}
</div>