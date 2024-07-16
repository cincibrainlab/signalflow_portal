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
        const ctx = document.getElementById('runsChart').getContext('2d');
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
    });

    // Stats dummy data
    let averageRuntime = "2.5 hours";
    let completionPercentage = "75%";

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
  
<main class="max-w-7xl mx-auto p-4">
    <header class="text-center mb-6">
        <h1 class="text-3xl font-bold">Dashboard</h1>
    </header>
    <div class="flex">
        <div class="w-2/3 grid grid-cols-1 md:grid-cols-2 gap-6 mr-6">
            <section class="md:col-span-1 bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Current Runs</h2>
                <canvas id="runsChart"></canvas>
            </section>
            <section class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Failed Files</h2>
                <ul class="space-y-2">
                    {#each failedFiles as file (file.id)}
                        <li class="flex items-center justify-between">
                            <span>{file.name}</span>
                            <button on:click={() => retryFile(file.id)} class="bg-yellow-500 text-white px-2 py-1 rounded text-sm">Retry</button>
                        </li>
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
                        <li class="flex items-center justify-between">
                            <span>{file.name}</span>
                            <button on:click={() => addFile(file.id)} class="bg-green-500 text-white px-2 py-1 rounded text-sm">Add to Analysis</button>
                        </li>
                    {/each}
                </ul>
            </section>
        </div>
        <div class="w-1/3">
            <section class="bg-white rounded-lg shadow p-6 h-full">
                <h2 class="text-xl font-semibold mb-4">Files</h2>
                <ul class="space-y-2">
                    {#each files as file (file.id)}
                        <li class="flex items-center justify-between">
                            <span>{file.name} - {file.status}</span>
                            <div>
                                <button on:click={() => viewDetails(file.id)} class="bg-blue-500 text-white px-2 py-1 rounded text-sm mr-2">View Details</button>
                                <button on:click={() => removeFile(file.id)} class="bg-red-500 text-white px-2 py-1 rounded text-sm">Remove</button>
                            </div>
                        </li>
                    {/each}
                </ul>
            </section>
        </div>
    </div>
</main>