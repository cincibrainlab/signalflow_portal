<script lang="ts">
    // Import necessary components and data

    import { onMount, onDestroy } from 'svelte';
    import pako from 'pako';
    import { flip } from 'svelte/animate';
    import { dndzone } from 'svelte-dnd-action';
    import { getOriginalFileFromUploadID, getParticipant, getEEGData} from '$lib/services/apiService';
    import { Line } from 'svelte-chartjs';

    export let upload_id: string;
    let File: any = [];
    let Participant: any = [];
    let EEGData: any[][] = [];

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
                EEGData = response ?? [];
                console.log('EEGData', EEGData);
                drawEEGPlot();
            });

        } else {
            console.error('No upload ID provided');
        }

        

    });

    function drawEEGPlot() {
        const canvas = document.getElementById('eegCanvas');
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        const channelHeight = height / 128;

        ctx.clearRect(0, 0, width, height);

        EEGData.forEach((channelData, channelIndex) => {
        ctx.beginPath();
        channelData.forEach((value, timeIndex) => {
            const x = (timeIndex / 1000) * width;
            const y = (channelIndex * channelHeight) + (value * channelHeight / 2);
            if (timeIndex === 0) {
            ctx.moveTo(x, y);
            } else {
            ctx.lineTo(x, y);
            }
        });
        ctx.stroke();
        });
    }

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
                <canvas id="eegCanvas" width="1000" height="1280"></canvas>
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
      border: 1px solid black;
    }
</style>