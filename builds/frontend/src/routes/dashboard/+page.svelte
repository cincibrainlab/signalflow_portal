<script lang="ts">
    import { goto } from '$app/navigation';
    import AnalysisDashboard from '$lib/components/AnalysisDashboard.svelte';
    import type { PageData } from './$types';

    export let data: PageData;

    function goBack() {
        goto('/analysisManager');
    }
</script>

<div class="p-4">
    <button on:click={goBack} class="mb-4 bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
        Back to Analysis Manager
    </button>
    {#if data.deploymentId}
        <AnalysisDashboard deploymentId={data.deploymentId} prefectStats={data.prefectStats} />
    {:else}
        <p>{data.error || 'No deployment ID provided.'}</p>
    {/if}
</div>