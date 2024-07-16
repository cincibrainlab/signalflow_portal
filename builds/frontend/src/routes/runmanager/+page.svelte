<script lang="ts">
    // Import necessary components and data


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

<main class="max-w-7xl mx-auto p-6 bg-gray-100 min-h-screen">
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
                <h2 class="text-2xl font-semibold mb-4 text-gray-700">Failed Files</h2>
                <ul class="space-y-3">
                    {#each failedFiles as file (file.id)}
                        <li class="bg-red-50 p-3 rounded-lg flex items-center justify-between">
                            <span class="text-red-700">{file.name}</span>
                            <button on:click={() => retryFile(file.id)} class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-md text-sm transition duration-300 ease-in-out">Retry</button>
                        </li>
                    {/each}
                </ul>
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
                <h2 class="text-2xl font-semibold mb-4 text-gray-700">Possible Files</h2>
                <ul class="space-y-3">
                    {#each possibleFiles as file (file.id)}
                        <li class="bg-blue-50 p-3 rounded-lg flex items-center justify-between">
                            <span class="text-blue-700">{file.name}</span>
                            <button on:click={() => addFile(file.id)} class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md text-sm transition duration-300 ease-in-out">Add to Analysis</button>
                        </li>
                    {/each}
                </ul>
            </section>
        </div>
        <div class="lg:w-1/3">
            <section class="bg-white rounded-xl shadow-md p-6 h-full transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-2xl font-semibold mb-4 text-gray-700">Files</h2>
                <ul class="space-y-3">
                    {#each files as file (file.id)}
                        <li class="bg-gray-50 p-3 rounded-lg">
                            <div class="flex items-center justify-between mb-2">
                                <span class="font-medium text-gray-800">{file.name}</span>
                                <span class="text-sm text-gray-500">{file.status}</span>
                            </div>
                            <div class="flex justify-end space-x-2">
                                <button on:click={() => viewDetails(file.id)} class="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded-md text-sm transition duration-300 ease-in-out">View Details</button>
                                <button on:click={() => removeFile(file.id)} class="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded-md text-sm transition duration-300 ease-in-out">Remove</button>
                            </div>
                        </li>
                    {/each}
                </ul>
            </section>
        </div>
    </div>
</main>
  
<!-- <main class="max-w-7xl mx-auto p-4">
    <header class="text-center mb-6">
        <h1 class="text-3xl font-bold">Dashboard</h1>
    </header>
    <div class="flex">
        <div class="w-2/3 grid grid-cols-1 md:grid-cols-2 gap-6 mr-6">
            <section class="md:col-span-1 bg-white rounded-lg shadow p-6 rounded-md">
                <h2 class="text-xl font-semibold mb-4">Current Runs</h2>
                <canvas id="runsChart"></canvas>
            </section>
            <section class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Failed Files</h2>
                <ul class="space-y-2">
                    {#each failedFiles as file (file.id)}
                        <section class="bg-gray-400 p-2 rounded-md">
                            <li class="flex items-center justify-between">
                                <span>{file.name}</span>
                                <button on:click={() => retryFile(file.id)} class="bg-yellow-500 text-white px-2 py-1 rounded text-sm">Retry</button>
                            </li>
                        </section>
                    {/each}
                </ul>
            </section>
            <section class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Stats</h2>
                <p class="mb-2">Average Runtime: {averageRuntime}</p>
                <p>Completion Percentage: {completionPercentage}</p>
            </section>
            <section class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Possible Files</h2>
                <ul class="space-y-2">
                    {#each possibleFiles as file (file.id)}
                        <section class="bg-gray-400 p-2 rounded-md">
                            <li class="flex items-center justify-between">
                                <span>{file.name}</span>
                                <button on:click={() => addFile(file.id)} class="bg-green-500 text-white px-2 py-1 rounded text-sm">Add to Analysis</button>
                            </li>
                        </section>
                    {/each}
                </ul>
            </section>
        </div>
        <div class="w-1/3">
            <section class="bg-white rounded-lg shadow p-6 h-full">
                <h2 class="text-xl font-semibold mb-4">Files</h2>
                <ul class="space-y-2">
                    {#each files as file (file.id)}
                        <section class="bg-gray-400 p-2 rounded-md">
                            <li class="flex items-center justify-between">
                                <span>{file.name} - {file.status}</span>
                                <div>
                                    <button on:click={() => viewDetails(file.id)} class="bg-blue-500 text-white px-2 py-1 rounded text-sm mr-2">View Details</button>
                                    <button on:click={() => removeFile(file.id)} class="bg-red-500 text-white px-2 py-1 rounded text-sm">Remove</button>
                                </div>
                            </li>
                        </section>
                    {/each}
                </ul>
            </section>
        </div>
    </div>
</main> -->