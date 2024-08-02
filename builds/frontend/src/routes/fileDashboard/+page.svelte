<script lang="ts">
    import { goto } from '$app/navigation';
    // This is a weird error, but it works so whatever
    import FileDashboardComponent from '$lib/components/FileDashboardComponent.svelte';
    import type { PageData } from './$types';

    export let data: PageData;

    function goBack() {
        goto('/vault');
    }
</script>

<div class="p-4">
    <button on:click={goBack} class="mb-4 bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
        Back to Vault
    </button>
    {#if data.upload_id}
        <FileDashboardComponent {data} />
    {:else}
        <p>{data.error || 'No deployment ID provided.'}</p>
    {/if}
</div>