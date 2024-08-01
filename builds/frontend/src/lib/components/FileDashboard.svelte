<script lang="ts">
    // Import necessary components and data

    import { onMount} from 'svelte';
    import { getOriginalFileFromUploadID, getParticipant, getEEGData} from '$lib/services/apiService';

    export let upload_id: string;
    let File: any = [];
    let Participant: any = [];
    let EEGData: any[][] = [];
    let Yscale = 1;

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
        const canvas: HTMLCanvasElement = document.getElementById('eegCanvas') as HTMLCanvasElement;
        if (canvas) {
            const ctx = canvas.getContext('2d');
            if (ctx) {
                let ParentComponenetWidth = canvas.parentElement ? canvas.parentElement.clientWidth : 0;
                
                canvas.width = EEGData[0].length;
                console.log('canvas.width', canvas.width);
                canvas.height = EEGData.length * 100;
                const width = canvas.width;
                const height = canvas.height;
                const channelHeight = height / (EEGData.length + 1);

                let samplesPerSecond = 100;
                
                let Xscale = ParentComponenetWidth / samplesPerSecond * 5;

                ctx.clearRect(0, 0, width, height);

                // Make labels for each channel
                EEGData.forEach((channelData, channelIndex) => {
                    ctx.font = '12px Arial';
                    ctx.fillText(`Channel ${channelIndex + 1}`, 0, channelHeight * (channelIndex + 1));
                });

                // Show border lines for each channel
                // EEGData.forEach((channelData, channelIndex) => {
                //     ctx.beginPath();
                //     const y = channelHeight * (channelIndex + 1);
                //     const ytop = y - (channelHeight / 2);
                //     const ybottom = y + (channelHeight / 2);
                //     ctx.moveTo(0, ytop);
                //     ctx.lineTo(width, ytop);
                //     ctx.stroke()

                //     ctx.moveTo(0, ybottom);
                //     ctx.lineTo(width, ybottom);
                //     ctx.stroke()
                // });

                EEGData.forEach((channelData, channelIndex) => {
                    // console.log('channel: ', channelIndex,' channelData', channelData);
                    ctx.beginPath();

                    // Normalize the data to fit the canvas


                    channelData.forEach((value, timeIndex) => {
                        const x = timeIndex * width / channelData.length;
                        // Set the y position to start at a constant distance apart 
                        let StartPoint = channelHeight * (channelIndex + 1);
                        // each channel needs to stay in own area so we need to adjust the y position
                        const ytop = StartPoint - (channelHeight / 2);
                        const ybottom = StartPoint + (channelHeight / 2);

                        // The y needs to stay within the channel area
                        value = value * 1000000;
                        
                        const y = StartPoint + ((value * Yscale)) ;

                        if (timeIndex === 0) {
                            ctx.moveTo(x, y);
                        } else {
                            ctx.lineTo(x, y);
                        }
                        
                    });
                    ctx.stroke();
                });
            }
        }
    }
    

    function ChangeScale() {
        drawEEGPlot();
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
                <div class="w-full h-96 overflow-x-scroll overflow-y-scroll border border-black">
                    <canvas id="eegCanvas"></canvas>
                </div>
                <div class="mt-4">
                    <label for="scaleInput" class="block text-sm font-medium text-gray-700">Scale:</label>
                    <input type="number" id="scaleInput" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" bind:value={Yscale}>
                    <button class="mt-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" on:click={ChangeScale}>Change Scale</button>
                </div>
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