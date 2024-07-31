<script lang="ts">
    import { goto } from '$app/navigation';
    import FileDashboard from '$lib/components/FileDashboard.svelte';
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
        <FileDashboard upload_id={data.upload_id} />
    {:else}
        <p>{data.error || 'No deployment ID provided.'}</p>
    {/if}
</div>