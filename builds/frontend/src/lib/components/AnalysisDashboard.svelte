<script lang="ts">
    // Import necessary components and data

    import { onMount, onDestroy } from 'svelte';
    import { flip } from 'svelte/animate';
    import { dndzone } from 'svelte-dnd-action';
    import { fetchPrefectStats, type PrefectStats } from '$lib/services/prefectAPI';

    export let data;
    let { prefectStats, analysis, analysisFlow, possibleFiles, deploymentId } = data;

    // Files dummy data
    let files: { id: string; name: string; status: string }[] = [];
    let pendingFiles: { id: string; name: string; status: string }[] = [];
    let failedFiles: { id: string; name: string; status: string }[] = [];
    let removedFileIds: Set<string> = new Set();

    // Stats data
    $: averageRuntime = prefectStats?.avg_runtime || '0';
    $: runsCompleted = prefectStats?.completed_runs || 0;
    $: totalRunsScheduled = prefectStats?.total_runs || 0;
    $: successRate = prefectStats?.success_rate?.toFixed(2) || '0';

    function handleDndConsider(e: CustomEvent) {
        pendingFiles = e.detail.items;
    }

    function handleDndFinalize(e: CustomEvent) {
        pendingFiles = e.detail.items;
    }

    function processFile(id: string) {
        // Implement your file processing logic here
        console.log(`Processing file with id: ${id}`);
    }

    function openDashboard(id: string) {
      goto(`/fileDashboard?id=${id}`);
  }


    // Runs dummy data
    import { Chart } from 'chart.js/auto';
	import { goto } from '$app/navigation';

    let chart: Chart<"doughnut", number[], string>;
    let chartData = {
        labels: ['Failed', 'Pending', 'Completed'],
        datasets: [{
            data: [
                prefectStats?.failed_runs || 0,
                prefectStats?.pending_runs || 0,
                prefectStats?.completed_runs || 0
            ],
            backgroundColor: ['#ff6b6b', '#feca57', '#48dbfb']
        }]
    };

    let intervalId: ReturnType<typeof setTimeout>;

    async function updatePrefectStats() {
        try {
            const newPrefectStats: PrefectStats = await fetchPrefectStats(deploymentId);
            
            // Update prefectStats (this will trigger the reactive statements)
            prefectStats = newPrefectStats;

            // Manually update the more complex derived data
            failedFiles = newPrefectStats.runs
                .filter(run => run.status === 'FAILED')
                .map(run => ({id: run.id, name: run.name, status: run.status}));

            pendingFiles = newPrefectStats.runs
                .filter(run => run.status === 'PENDING' || run.status === 'SCHEDULED')
                .map(run => ({id: run.id, name: run.name, status: run.status}));

            files = newPrefectStats.runs
                .filter(run => !removedFileIds.has(run.id))
                .map(run => ({id: run.id, name: run.name, status: run.status}));

            // Update chart data
            chartData.datasets[0].data = [
                newPrefectStats.failed_runs,
                newPrefectStats.pending_runs,
                newPrefectStats.completed_runs
            ];
            chart.update();

        } catch (error) {
            console.error('Error updating Prefect stats:', error);
        }
    }

    onMount(async () => {
        try {
            const ctx = (document.getElementById('runsChart') as HTMLCanvasElement)!.getContext('2d');
            if (ctx) {
                chart = new Chart(ctx, {
                    type: 'doughnut',
                    data: chartData,
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom',
                            },
                            title: {
                                display: true,
                                text: 'Current Runs'
                            }
                        }
                    }
                });
            }
            // Initialize files, pendingFiles, and failedFiles
            if (prefectStats) {
                files = prefectStats.runs.map((run: { id: string; name: string; status: string }) => ({id: run.id, name: run.name, status: run.status}));
                pendingFiles = prefectStats.runs.filter((run: { id: string; name: string; status: string }) => run.status === 'PENDING' || run.status === 'SCHEDULED').map((run: { id: string; name: string; status: string }) => ({id: run.id, name: run.name, status: run.status}));
                failedFiles = prefectStats.runs.filter((run: { id: string; name: string; status: string }) => run.status === 'FAILED').map((run: { id: string; name: string; status: string }) => ({id: run.id, name: run.name, status: run.status}));
            }
            // Set up periodic refresh
            intervalId = setInterval(updatePrefectStats, 500);

        } catch (error) {
            console.error('Error in onMount:', error);
            // Handle the error appropriately (e.g., show an error message to the user)
        }
    });

    onDestroy(() => {
        // Clear the interval when the component is destroyed
        if (intervalId) {
            clearInterval(intervalId);
        }
    });

    function removeFile(id: string) {
        removedFileIds.add(id);
        files = files.filter(file => file.id !== id);
    }

    function viewDetails(id: string) {
        // Implement view details functionality
        console.log(`Viewing details for file ${id}`);
    }

    function retryFile(id: string) {
        // Implement retry functionality
        console.log(`Retrying file ${id}`);
    }

    function addFile(id: number) {
        // Implement add file functionality
        console.log(`Adding file ${id} to analysis`);
    }


</script>

<main class="w-11/12 mx-auto p-6 min-h-screen">
    <header class="text-center mb-8">
        <h1 class="text-4xl font-bold ">Dashboard</h1>
        <span class="text-2xl font-bold">Flow Name: {analysisFlow.name}</span>
    </header>
    <div class="flex flex-col lg:flex-row gap-6">
        <div class="lg:w-1/2 grid grid-cols-1 md:grid-cols-2 gap-6">
            <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-2xl font-semibold mb-4 ">Current Runs</h2>
                <canvas id="runsChart" class="w-full"></canvas>
            </section>
            <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-2xl font-semibold mb-6 ">Stats</h2>
                <div class="grid grid-cols-2 gap-4 h-64">
                    <div class="bg-purple-50 p-4 rounded-lg flex flex-col justify-between">
                        <p class="text-sm text-purple-600 mb-1">Total Runs Scheduled</p>
                        <p class="text-2xl font-bold text-purple-800">{totalRunsScheduled}</p>
                    </div>
                    <div class="bg-yellow-50 p-4 rounded-lg flex flex-col justify-between">
                        <p class="text-sm text-yellow-600 mb-1">Runs Completed</p>
                        <p class="text-2xl font-bold text-yellow-800">{runsCompleted}</p>
                    </div>
                    <div class="bg-blue-50 p-4 rounded-lg flex flex-col justify-between">
                        <p class="text-sm text-blue-600 mb-1">Average Runtime</p>
                        <p class="text-2xl font-bold text-blue-800">{averageRuntime}</p>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg flex flex-col justify-between">
                        <p class="text-sm text-green-600 mb-1">Success Rate</p>
                        <p class="text-2xl font-bold text-green-800">{successRate}%</p>
                    </div>
                </div>
            </section>
            <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-xl font-semibold mb-2 ">Failed Files</h2>
                <div class="h-48 overflow-y-auto">
                    <table class="w-full text-sm">
                        <thead class=" sticky top-0">
                            <tr>
                                <th class="p-2 text-left">Name</th>
                                <th class="p-2 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each failedFiles as file (file.id)}
                                <tr class="border-b">
                                    <td class="p-2 text-red-700">{file.name}</td>
                                    <td class="p-2 text-right">
                                        <button on:click={() => retryFile(file.id)} class="bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-xs">Retry</button>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </section>
            <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-xl font-semibold mb-2 ">Pending Files</h2>
                <div class="h-48 overflow-y-auto">
                    <table class="w-full text-sm">
                        <thead class=" sticky top-0">
                            <tr>
                                <th class="p-2 text-left">Name</th>
                                <th class="p-2 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody use:dndzone={{items: pendingFiles, flipDurationMs: 300}} on:consider={handleDndConsider} on:finalize={handleDndFinalize}>
                            {#each pendingFiles as file (file.id)}
                                <tr animate:flip={{duration: 300}} class="border-b cursor-move">
                                    <td class="p-2 text-yellow-800">⋮⋮ {file.name}</td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </section>
            
            
        </div>
        <div class="lg:w-1/2">
            <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 h-full transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-xl font-semibold mb-2 ">Files</h2>
                <div class="overflow-y-auto">
                    <table class="w-full text-sm">
                        <thead class=" sticky top-0">
                            <tr>
                                <th class="p-2 text-left">Name</th>
                                <th class="p-2">Status</th>
                                <th class="p-2 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each files as file (file.id)}
                                <tr class="border-b">
                                    <td class="p-2 font-medium">{file.name}</td>
                                    <td class="p-2 text-center">{file.status}</td>
                                    <td class="p-2 text-right">
                                        <button on:click={(event) => {event.stopPropagation(); openDashboard(file.upload_id)}} class="bg-indigo-600 hover:bg-indigo-700 text-white px-2 py-1 rounded text-xs mr-1">Results</button>
                                        <button on:click={() => removeFile(file.id)} class="bg-gray-600 hover:bg-gray-700 text-white px-2 py-1 rounded text-xs">Remove</button>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </section>
        </div>
        
    </div>
    <div class="w-full mt-6">
        <section class="dark:bg-white rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
            <h2 class="text-xl font-semibold mb-2 text-gray-700">Possible Files</h2>
            <div class="h-48 overflow-y-auto">
                <table class="w-full text-sm">
                    <thead class=" sticky top-0">
                        <tr>
                            <th class="p-2 text-left">Name</th>
                            <th class="p-2 text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each possibleFiles as newFile}
                            <tr class="border-b">
                                <td class="p-2 text-blue-700">{newFile.original_name}</td>
                                <td class="p-2 text-right">
                                    <button on:click={() => addFile(newFile.id)} 
                                            class="bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded text-xs transition duration-300 ease-in-out">
                                        Add to Analysis
                                    </button>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </section>
    </div>
    <div class="w-full mt-6">
        <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
            <h2 class="text-xl font-semibold mb-4 ">Utilities</h2>
            <div class="flex justify-start space-x-4">
                <button class="bg-blue-600 hover:bg-blue-800 text-white font-semibold py-2 px-4 rounded transition ease-in-out duration-300">
                    Download CSV
                </button>
                <button class="bg-green-600 hover:bg-green-800 text-white font-semibold py-2 px-4 rounded transition ease-in-out duration-300">
                    Download All Files
                </button>
            </div>
        </section>
    </div>
</main>

  
<!-- Have an area that shows duplicate files and participants -->