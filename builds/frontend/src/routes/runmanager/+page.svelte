<script lang="ts">
    // Import necessary components and data

    import { flip } from 'svelte/animate';
    import { dndzone } from 'svelte-dnd-action';

    let pendingFiles = [
        { id: 1, name: "document1.pdf" },
        { id: 2, name: "image1.jpg" },
        { id: 3, name: "spreadsheet1.xlsx" },
        { id: 4, name: "presentation1.pptx" }
    ];

    function handleDndConsider(e: CustomEvent) {
        pendingFiles = e.detail.items;
    }

    function handleDndFinalize(e: CustomEvent) {
        pendingFiles = e.detail.items;
    }

    function processFile(id: number) {
        // Implement your file processing logic here
        console.log(`Processing file with id: ${id}`);
    }


    // Runs dummy data
    import { Chart } from 'chart.js/auto';
    import { onMount } from 'svelte';

    let chart;
    let chartData = {
        labels: ['Failed', 'Pending', 'Completed'],
        datasets: [{
            data: [3, 5, 10],
            backgroundColor: ['#ff6b6b', '#feca57', '#48dbfb']
        }]
    };

    onMount(() => {
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
    });

    // Stats dummy data
    let averageRuntime = '2.5s';
    let completionPercentage = 85;
    let totalFilesProcessed = 1234;
    let successRate = 92;
    let performanceTrend = 3.5;

    // Files dummy data
    let files = [
        { id: 1, name: 'file1.txt', status: 'completed' },
        { id: 2, name: 'file2.txt', status: 'pending' },
        { id: 3, name: 'file3.txt', status: 'completed' },
    ];

    function removeFile(id: number) {
        files = files.filter(file => file.id !== id);
    }

    function viewDetails(id: number) {
        // Implement view details functionality
        console.log(`Viewing details for file ${id}`);
    }

    // Failed files dummy data
    let failedFiles = [
        { id: 1, name: 'failed1.txt' },
        { id: 2, name: 'failed2.txt' },
    ];

    function retryFile(id: number) {
        // Implement retry functionality
        console.log(`Retrying file ${id}`);
    }

    // Possible files dummy data
    let possibleFiles = [
        { id: 1, name: 'possible1.txt' },
        { id: 2, name: 'possible2.txt' },
        { id: 3, name: 'possible3.txt' },
    ];

    function addFile(id: number) {
        // Implement add file functionality
        console.log(`Adding file ${id} to analysis`);
    }

</script>

<main class="w-11/12 mx-auto p-6 bg-gray-100 min-h-screen">
    <header class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-800">Dashboard</h1>
    </header>
    <div class="flex flex-col lg:flex-row gap-6">
        <div class="lg:w-2/3 grid grid-cols-1 md:grid-cols-2 gap-6">
            <section class="bg-white rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-2xl font-semibold mb-4 text-gray-700">Current Runs</h2>
                <canvas id="runsChart" class="w-full"></canvas>
            </section>
            <section class="bg-white rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-2xl font-semibold mb-6 text-gray-700">Stats</h2>
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-blue-50 p-4 rounded-lg">
                        <p class="text-sm text-blue-600 mb-1">Average Runtime</p>
                        <p class="text-2xl font-bold text-blue-800">{averageRuntime}</p>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg">
                        <p class="text-sm text-green-600 mb-1">Completion Rate</p>
                        <p class="text-2xl font-bold text-green-800">{completionPercentage}%</p>
                    </div>
                    <div class="bg-purple-50 p-4 rounded-lg">
                        <p class="text-sm text-purple-600 mb-1">Total Files Processed</p>
                        <p class="text-2xl font-bold text-purple-800">{totalFilesProcessed}</p>
                    </div>
                    <div class="bg-yellow-50 p-4 rounded-lg">
                        <p class="text-sm text-yellow-600 mb-1">Success Rate</p>
                        <p class="text-2xl font-bold text-yellow-800">{successRate}%</p>
                    </div>
                </div>
                <div class="mt-6 bg-gray-50 p-4 rounded-lg">
                    <h3 class="text-lg font-semibold mb-2 text-gray-700">Performance Trend</h3>
                    <div class="flex items-center">
                        <span class="text-2xl font-bold text-gray-800 mr-2">{performanceTrend}</span>
                        {#if performanceTrend > 0}
                            <svg class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                            </svg>
                        {:else}
                            <svg class="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                            </svg>
                        {/if}
                    </div>
                    <p class="text-sm text-gray-600 mt-1">Compared to last week</p>
                </div>
            </section>
            <section class="bg-white rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-xl font-semibold mb-2 text-gray-700">Failed Files</h2>
                <div class="h-48 overflow-y-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-50 sticky top-0">
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
            <section class="bg-white rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-xl font-semibold mb-2 text-gray-700">Pending Files</h2>
                <div class="h-48 overflow-y-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-50 sticky top-0">
                            <tr>
                                <th class="p-2 text-left">Name</th>
                                <th class="p-2 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody use:dndzone={{items: pendingFiles, flipDurationMs: 300}} on:consider={handleDndConsider} on:finalize={handleDndFinalize}>
                            {#each pendingFiles as file (file.id)}
                                <tr animate:flip={{duration: 300}} class="border-b cursor-move">
                                    <td class="p-2 text-yellow-800">⋮⋮ {file.name}</td>
                                    <td class="p-2 text-right">
                                        <button on:click={() => processFile(file.id)} class="bg-yellow-500 hover:bg-yellow-600 text-white px-2 py-1 rounded text-xs">Process</button>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </section>
            
            
        </div>
        <div class="lg:w-1/3">
            <section class="bg-white rounded-xl shadow-md p-6 h-full transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-xl font-semibold mb-2 text-gray-700">Files</h2>
                <div class="h-48 overflow-y-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-50 sticky top-0">
                            <tr>
                                <th class="p-2 text-left">Name</th>
                                <th class="p-2">Status</th>
                                <th class="p-2 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each files as file (file.id)}
                                <tr class="border-b">
                                    <td class="p-2 font-medium text-gray-800">{file.name}</td>
                                    <td class="p-2 text-center text-gray-500">{file.status}</td>
                                    <td class="p-2 text-right">
                                        <button on:click={() => viewDetails(file.id)} class="bg-indigo-600 hover:bg-indigo-700 text-white px-2 py-1 rounded text-xs mr-1">View</button>
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
        <section class="bg-white rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
            <h2 class="text-xl font-semibold mb-2 text-gray-700">Possible Files</h2>
            <div class="h-48 overflow-y-auto">
                <table class="w-full text-sm">
                    <thead class="bg-gray-50 sticky top-0">
                        <tr>
                            <th class="p-2 text-left">Name</th>
                            <th class="p-2 text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each possibleFiles as file (file.id)}
                            <tr class="border-b">
                                <td class="p-2 text-blue-700">{file.name}</td>
                                <td class="p-2 text-right">
                                    <button on:click={() => addFile(file.id)} 
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
        <section class="bg-white rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
            <h2 class="text-xl font-semibold mb-4 text-gray-700">Utilities</h2>
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

<!-- Add utlities area 
 Download csv 
 Download all files
  -->
  
<!-- Have an area that shows duplicate files and participants -->