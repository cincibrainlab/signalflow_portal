<script lang="ts">
    // Import necessary components and data

    import { onMount, onDestroy } from 'svelte';
    import pako from 'pako';
    import { flip } from 'svelte/animate';
    import { dndzone } from 'svelte-dnd-action';
    import { getOriginalFileFromUploadID, getParticipant, getEEGData} from '$lib/services/apiService';
    import { Chart } from 'chart.js';

    export let upload_id: string;
    let File: any = [];
    let Participant: any = [];
    let labels:any = [];
    let canvas:any;
    let EEGData: any;

    onMount(async () => {
        if (upload_id) {
            getOriginalFileFromUploadID(upload_id).then((response) => {
                File = response;
                console.log('File', File)
                if (File.participant) {
                    getParticipant(File.participant).then((response) => {
                        Participant = response
                        console.log('participantData', Participant)
                    });
                }

            });
            
            getEEGData(upload_id).then((response) => {
                EEGData = response;
                console.log('EEGData', EEGData)
            });

        } else {
            console.error('No upload ID provided');
        }

        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
        type: 'line',
        data: {
            labels: EEGData.map((_: any, index: number) => index),
            datasets: [{
            label: 'EEG Data',
            data: EEGData,
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            fill: false
            }]
        },
        options: {
            scales: {
            x: {
                type: 'linear',
                position: 'bottom'
            }
            }
        }
        });

    });

    

    const chartData = {
        labels,
        datasets: [
        {
            label: 'EEG Data',
            EEGData,
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            fill: false
        }
        ]
    };

    const options = {
        scales: {
        x: {
            type: 'linear',
            position: 'bottom'
        }
        }
    };

</script>

<main class="w-11/12 mx-auto p-6 min-h-screen">
    <header class="text-center mb-8">
        <h1 class="text-4xl font-bold "> File Dashboard</h1>
        <h2 class="text-xl font-semibold ">Filename: {File.original_name}</h2>
    </header>
    <div class="flex flex-col lg:flex-row gap-6">
        <div class="lg:w-2/3 gap-6">
            <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-2xl font-semibold mb-4 ">n/a</h2>
                <h2 class="text-xl font-semibold mb-2 ">{EEGData}</h2>
                <canvas bind:this={canvas}></canvas>
            </section>
        </div>
        <div class="lg:w-1/3">
            <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 h-full transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-xl font-semibold mb-2 ">Participant Details</h2>
                <div class="flex flex-col gap-4">
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Participant ID:</span>
                        <span>{Participant.participant_id}</span>
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Species:</span>
                        <span>{Participant.species}</span>
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Age:</span>
                        <span>{Participant.age}</span>
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Age Group:</span>
                        <span>{Participant.age_group}</span>
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Gender:</span>
                        <span>{Participant.gender}</span>
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Handedness:</span>
                        <span>{Participant.handedness}</span>
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Diagnosis:</span>
                        <span>{Participant.diagnosis}</span>
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Anxiety Level:</span>
                        <span>{Participant.anxiety_level}</span>
                    </div>
            </section>
        </div>
        
    </div>
    <div class="w-full mt-6">
        <section class="dark:bg-white rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
            <h2 class="text-xl font-semibold mb-2 text-gray-700">Possible Files</h2>
        </section>
    </div>
    <div class="w-full mt-6">
        <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
            <h2 class="text-xl font-semibold mb-4 ">Utilities</h2>

        </section>
    </div>
</main>

  
<!-- Have an area that shows duplicate files and participants -->
<style>
    canvas {
      width: 100%;
      height: 400px;
    }
</style>