<script lang="ts">
    import type { PageData } from './$types';
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { getFileRuns } from '$lib/services/apiService';
    import { Button } from '$lib/components/ui/button';
    import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "$lib/components/ui/table";

    export let data: PageData;

    let fileRunId = data.fileRunId;
    let fileRun = data.fileRun;

    let activeTab = 0;
    const tabs = ['Table', 'Plots', 'Pdf'];

    function setActiveTab(index: number) {
        activeTab = index;
    }
</script>

<main class="container mx-auto p-4">
    <header class="text-center mb-2">
        <h1 class="text-4xl font-bold "> Results Details</h1>
        <p class="text-lg">{fileRunId}</p>
    </header>

    <div class="mb-4">
        <ul class="flex border-b">
            {#each tabs as tab, index}
                <li class="-mb-px mr-1">
                    <a
                        class="bg-white inline-block py-2 px-4 font-semibold {activeTab === index ? 'border-l border-t border-r rounded-t text-blue-700' : 'text-blue-500 hover:text-blue-800'}"
                        href="#{tab.toLowerCase().replace(' ', '-')}"
                        on:click|preventDefault={() => setActiveTab(index)}
                    >
                        {tab}
                    </a>
                </li>
            {/each}
        </ul>
    </div>
    <div class="">
        {#if activeTab === 0}
            <div class="p-4">
                <h2 class="text-2xl font-semibold mb-4">Test</h2>
                {#if fileRun}
                    <Table>
                        <TableBody>
                            <TableRow>
                                <TableCell>Analysis Name</TableCell>
                                <TableCell>{fileRun.analysis_name}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Status</TableCell>
                                <TableCell>{fileRun.status}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Created At</TableCell>
                                <TableCell>{fileRun.run_created_at}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Completed At</TableCell>
                                <TableCell>{fileRun.run_completed_at || 'N/A'}</TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                {:else}
                    <p>Loading file run data...</p>
                {/if}
            </div>
        {:else if activeTab === 1}
            <div class="p-4">
                <h2 class="text-2xl font-semibold mb-4">Data Visualization</h2>
                <!-- Placeholder for data visualization -->
                <p>Data visualization content goes here.</p>
            </div>
        {:else if activeTab === 2}
            <div class="p-4">
                <h2 class="text-2xl font-semibold mb-4">Raw Data</h2>
                <!-- Placeholder for raw data display -->
                <p>Raw data content goes here.</p>
            </div>
        {/if}
    </div>
</main>