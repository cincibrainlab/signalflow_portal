<!-- src/lib/components/FileDashboardComponent.svelte -->
<script lang="ts">
    // Import necessary components and data

    import { onMount, onDestroy } from 'svelte';
    import { getOriginalFileFromUploadID, getParticipant, getEEGData, downloadFile, getFileRuns, baseUrl, deleteTemporaryFile} from '$lib/services/apiService';
    import * as d3 from 'd3';
	import { Button } from './ui/button';
    import { ArrowBigLeft, ArrowBigRight, ArrowBigLeftDash, ArrowBigRightDash, ChevronDown } from 'lucide-svelte';
    import { Badge } from "$lib/components/ui/badge"
    import { Alert} from 'flowbite-svelte';
	import { fade } from 'svelte/transition';
    import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "$lib/components/ui/table"
	import { goto } from '$app/navigation';
    import { Checkbox } from "$lib/components/ui/checkbox"

    export let data;
    let upload_id: string = data.upload_id;
    let File: any = [];
    let Participant: any = [];
    let Derivatives: any = [];

    let EEGData: Float64Array[] = [];
    let numChannels: number = 0;
    let psdPath: string = '';

    let svgElement: SVGSVGElement;
    let width: number;
    let height: number;
    let xScale: d3.ScaleLinear<number, number>;
    let yScale: d3.ScaleLinear<number, number>;
    let xAxis: d3.Selection<SVGGElement, unknown, null, undefined>;
    let chartArea: d3.Selection<SVGGElement, unknown, null, undefined>;

    let yScaleRange = 50; // Default y-scale range in microvolts
    let samplingRate = 100; // Default sampling rate
    let numSecondsToDisplay = 5;
    let viewportStart = 0;
    let viewportEnd = numSecondsToDisplay * samplingRate; // Initial viewport size (numSecondsToDisplay seconds * samplingRate Hz = ? samples)
    

    let resizeObserver: ResizeObserver;

    let showAdvancedSettings = false;
    let showToast = false;
    let toastMessage = '';
    let toastType = 'success';

    let selectedChannels: number[] = [];

    async function openFile(filePath: string) {
        try {
            const url = await getFile(filePath);
            window.open(url, '_blank');
        } catch (error) {
            console.error('Error opening file:', error);
        }
    }

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
                getFileRuns(File._id).then((response) => {
                    Derivatives = response;
                    console.log('Derivatives', Derivatives);
                });

            });
            
            getEEGData(upload_id, samplingRate).then((response) => {
                EEGData = Array.isArray(response.data) ? response.data.map((arr: any[]) => new Float64Array(arr)) : [response ?? []] as Float64Array[];
                console.log('response', response);
                numChannels = response.num_channels;
                psdPath = response.psd_path;
                console.log('psdPath', psdPath);
                console.log('EEGData', EEGData);
                selectedChannels = Array.from({ length: numChannels }, (_, i) => i);
                drawEEGPlot();
                updateYScale(yScaleRange);
            });
        


        } else {
            console.error('No upload ID provided');
        }

        if (EEGData && EEGData.length > 0) {
            drawEEGPlot();
        }

        resizeObserver = new ResizeObserver(() => {
            drawEEGPlot();
        });

        resizeObserver.observe(svgElement);
    });

    onDestroy(() => {
        if (resizeObserver) {
            resizeObserver.disconnect();
        }
            // Remove the SVG content, but keep the element
        EEGData = [];
        
        if (svgElement != null) {
            while (svgElement.firstChild) {
                svgElement.removeChild(svgElement.firstChild);
            }
        }

        if (psdPath) {
            deleteTemporaryFile(psdPath.split('/').pop() || '').catch(error => {
                console.error('Error deleting temporary file:', error);
            });
        }
    });

    function drawEEGPlot() {
        const margin = { top: 20, right: 20, bottom: 30, left: 50 };
        width = svgElement.clientWidth - margin.left - margin.right;
        height = svgElement.clientHeight - margin.top - margin.bottom;

        // Clear any existing SVG content
        d3.select(svgElement).selectAll("*").remove();

        const svg = d3.select(svgElement)
            .attr("width", "100%")
            .attr("height", "100%")
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        xScale = d3.scaleLinear()
            .domain([viewportStart / samplingRate, viewportEnd / samplingRate])
            .range([0, width]);

        yScale = d3.scaleLinear()
            .domain([-yScaleRange / 2, yScaleRange / 2])
            .range([height, 0]);

        const channelHeight = height / selectedChannels.length;

        const clipPath = svg.append("defs").append("clipPath")
            .attr("id", "clip")
            .append("rect")
            .attr("width", width)
            .attr("height", height);

        chartArea = svg.append("g")
            .attr("clip-path", "url(#clip)");

        EEGData.forEach((channel, i) => {
            if (selectedChannels.includes(i)) {
                const yOffset = selectedChannels.indexOf(i) * channelHeight;

                const scaledLine = d3.line<number>()
                    .x((d, i) => xScale((viewportStart + i) / samplingRate))
                    .y(d => yOffset + channelHeight / 2 + (yScale(d) - yScale(0)) / EEGData.length);

                chartArea.append("path")
                    .datum(channel.slice(viewportStart, viewportEnd))
                    .attr("fill", "none")
                    .attr("stroke", d3.schemeCategory10[i % 10])
                    .attr("stroke-width", 1.5)
                    .attr("d", scaledLine);

                svg.append("text")
                    .attr("x", -10)
                    .attr("y", yOffset + channelHeight / 2)
                    .attr("dy", ".35em")
                    .attr("text-anchor", "end")
                    .text(`Ch ${i + 1}`);
            }
        });

        xAxis = svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale).tickFormat(d => `${Number(d).toFixed(2)}s`));

        svg.append("g")
            .attr("class", "y-axis")
            .call(d3.axisLeft(yScale));
    }

    function updateViewport(startSeconds: number, endSeconds: number) {
        viewportStart = Math.floor(startSeconds * samplingRate);
        viewportEnd = Math.floor(endSeconds * samplingRate);
        xScale.domain([startSeconds, endSeconds]);
        xAxis.call(d3.axisBottom(xScale).tickFormat(d => `${Number(d).toFixed(2)}s`));

        // Instead of calling drawEEGPlot, update only the necessary parts
        updateEEGLines();
    }

    function updateEEGLines() {
        const height = svgElement.clientHeight - 50; // Subtracting 50 to account for margins
        const channelHeight = height / selectedChannels.length;

        chartArea.selectAll("path")
            .data(EEGData)
            .attr("d", (channel, i) => {
                if (selectedChannels.includes(i)) {
                    const yOffset = selectedChannels.indexOf(i) * channelHeight;
                    return d3.line<number>()
                        .x((d, i) => xScale((viewportStart + i) / samplingRate))
                        .y(d => yOffset + channelHeight / 2 + (yScale(d) - yScale(0)) / EEGData.length)(channel.slice(viewportStart, viewportEnd));
                }
                return '';
            });
    }

    function updateYScale(newRange: number) {
        yScaleRange = newRange;
        yScale.domain([-yScaleRange / 2000000, yScaleRange / 2000000]);
        
        // Update y-axis
        d3.select<SVGSVGElement, unknown>(svgElement).select<SVGSVGElement>(".y-axis")
            .call(d3.axisLeft(yScale));

        // Update EEG lines
        updateEEGLines();
    }

    function handleToast(message: string, type: string) {
        showToast = true;
        toastMessage = message;
        toastType = type;
        setTimeout(() => showToast = false, 3000);
    }

    function updateSamplingRate(newRate: number) {
        handleToast(`Fetching data at ${newRate} Hz`, 'success');
        samplingRate = newRate;
        viewportEnd = viewportStart + numSecondsToDisplay * samplingRate;
        getEEGData(upload_id, samplingRate).then((response) => {
            EEGData = Array.isArray(response.data) ? response.data.map((arr: any[]) => new Float64Array(arr)) : [response ?? []] as Float64Array[];
            numChannels = response.num_channels;
            console.log('EEGData', EEGData);
            drawEEGPlot();
            updateYScale(yScaleRange);
            handleToast(`Data fetched at ${newRate} Hz`, 'success');
        }).catch((error) => {
            handleToast(`Error fetching data at ${newRate} Hz`, 'error');
        });
    }

    function updateNumSecondsToDisplay(newNumSeconds: number) {
        numSecondsToDisplay = newNumSeconds;
        viewportEnd = viewportStart + numSecondsToDisplay * samplingRate;
        updateViewport(0,newNumSeconds)
    }

    function navigateViewport(seconds: number) {
        const currentStart = viewportStart / samplingRate;
        const currentEnd = viewportEnd / samplingRate;
        const duration = currentEnd - currentStart;
        
        let newStart = currentStart + seconds;
        let newEnd = currentEnd + seconds;

        // Ensure we don't go beyond the data bounds
        if (newStart < 0) {
            newStart = 0;
            newEnd = duration;
        } else if (newEnd > EEGData[0].length / samplingRate) {
            newEnd = EEGData[0].length / samplingRate;
            newStart = newEnd - duration;
        }

        updateViewport(newStart, newEnd);
    }

    function downlaodEEGFIle() {
        downloadFile(upload_id);
    }

    function toggleChannel(channelIndex: number) {
        if (selectedChannels.includes(channelIndex)) {
            selectedChannels = selectedChannels.filter(ch => ch !== channelIndex);
        } else {
            selectedChannels = [...selectedChannels, channelIndex].sort((a, b) => a - b);
        }
        drawEEGPlot();
    }

</script>

<main class="w-11/12 mx-auto p-6 min-h-screen">
    <header class="text-center mb-2">
        <h1 class="text-4xl font-bold "> Recording Details</h1>
        <h2 class="text-xl font-semibold ">Filename: {File.original_name}</h2>
    </header>
    {#if File.tags}
    <div class="text-center mb-4">
        <span class="text-xl font-semibold">Tags:</span>
        <div class="flex flex-wrap justify-center gap-2 mt-2">
            {#each File.tags as tag}
                <Badge class="{tag.text_class} text-base" style="background-color: {tag.color};">{tag.name}</Badge>
            {/each}
        </div>
    </div>
    {/if}
    <div class="flex flex-col gap-6">
        <div class="w-full">
            <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                <div class="w-full overflow-x-scroll overflow-y-scroll border border-black">
                    <div class="w-full h-[500px]">
                        <svg bind:this={svgElement} width="100%" height="100%"></svg>
                    </div>
                </div>
                <div class="flex justify-between mt-4">
                    <div>
                        <div class="flex gap-2">
                            <label for="scaleInput" class="block text-base font-medium text-gray-700">Scale (µV):</label>
                            <input type="number" id="scaleInput" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" bind:value={yScaleRange} 
                            on:input={() => updateYScale(yScaleRange)}>
                        </div>
                        <div class="flex gap-2 mt-4">
                            <Button on:click={() => updateYScale(15)}>15 µV</Button>
                            <Button on:click={() => updateYScale(50)}>50 µV</Button>
                            <Button on:click={() => updateYScale(100)}>100 µV</Button>
                        </div>
                    </div>
                    <div>
                        <div class="flex gap-2">
                            <label for="numSecondsInput" class="block text
                            -base font-medium text-gray-700">Seconds to Display:</label>
                            <input type="number" id="numSecondsInput" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" bind:value={numSecondsToDisplay}
                            on:input={() => updateNumSecondsToDisplay(numSecondsToDisplay)}>
                        </div>
                        <div class="flex justify-center gap-2 mt-4">
                            <Button on:click={() => navigateViewport(-5)}><ArrowBigLeftDash/>5s</Button>
                            <Button on:click={() => navigateViewport(-1)}><ArrowBigLeft/>1s</Button>
                            <Button on:click={() => navigateViewport(1)}>1s<ArrowBigRight/></Button>
                            <Button on:click={() => navigateViewport(5)}>5s<ArrowBigRightDash/></Button>
                        </div>
                    </div>
                    <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                        <h2 class="text-xl font-semibold mb-4">Channel Selection</h2>
                        <div class="grid grid-cols-4 gap-4">
                            {#each Array(numChannels) as _, i}
                                <div class="flex items-center space-x-2">
                                    <Checkbox 
                                        id="channel-{i}" 
                                        checked={selectedChannels.includes(i)}
                                        onCheckedChange={() => toggleChannel(i)}
                                    />
                                    <label
                                        for="channel-{i}"
                                        class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                                    >
                                        Channel {i + 1}
                                    </label>
                                </div>
                            {/each}
                        </div>
                    </section>
                </div>

                <div class="mt-8">
                    <button
                        class="w-full flex items-center justify-between text-xl font-semibold text-gray-700 hover:text-gray-900 focus:outline-none"
                        on:click={() => showAdvancedSettings = !showAdvancedSettings}
                    >
                        <span>Advanced Settings</span>
                        <div class="transition-transform duration-200" class:rotate-180={showAdvancedSettings}>
                            <ChevronDown class="w-6 h-6" />
                        </div>
                    </button>
            
                    {#if showAdvancedSettings}
                        <div transition:fade={{ duration: 200 }}>
                            <div class="mt-4 flex gap-2">
                                <label for="samplingRateInput" class="block text-base font-medium text-gray-700">Sampling Rate (Hz):</label>
                                <input type="number" id="samplingRateInput" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" bind:value={samplingRate} 
                                on:keydown={(e) => e.key === 'Enter' && updateSamplingRate(samplingRate)}>
                            </div>
                            <!-- Add more advanced settings here as needed -->
                        </div>
                    {/if}
                </div>

            </section>
        </div>
        {#if psdPath}
            <div class="w-full mt-6">
                <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                    <h2 class="text-xl font-semibold mb-4">Power Spectral Density</h2>
                    {#if psdPath}
                        <img 
                            src={`${baseUrl}get-temp-file/${encodeURIComponent(psdPath.split('/').pop() || '')}`} 
                            alt="Power Spectral Density Graph" 
                            class="w-full h-auto" 
                            on:error={(e) => console.error('Image load error:', e)}
                        />
                    {:else}
                        <p>PSD graph not available</p>
                    {/if}
                </section>
            </div>
        {/if}
        <div class="w-full">
            <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 h-full transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-xl font-semibold mb-2 ">Participant Details</h2>
                <div class="grid grid-cols-3 gap-4">
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Participant ID:</span>
                        <span>{Participant.participant_id}</span>
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Group:</span>
                        <span>{Participant.diagnosis}</span>
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Type:</span>
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
                        <span class="font-semibold">Sex:</span>
                        <span>{Participant.gender}</span>
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Handedness:</span>
                        <span>{Participant.handedness}</span>
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="font-semibold">Anxiety Level:</span>
                        <span>{Participant.anxiety_level}</span>
                    </div>
                </div>
                
            </section>
        </div>
        <div class="w-full">
            <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 h-full transition duration-300 ease-in-out hover:shadow-lg">
                <h2 class="text-xl font-semibold mb-2 ">Derivatives</h2>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Job Name</TableHead>
                            <TableHead>Flow Name</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Created At</TableHead>
                            <TableHead>Completed At</TableHead>
                            <TableHead>#Outputs</TableHead>
                            <TableHead>Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {#each Derivatives as Derivative}
                        <TableRow>
                            <TableCell>{Derivative.analysis_name}</TableCell>
                            <TableCell>{Derivative.flow_name}</TableCell>
                            <TableCell>
                                <Badge class="{
                                  Derivative.status === 'completed' ? 'bg-green-500' : 
                                  Derivative.status === 'pending' ? 'bg-yellow-500' : 
                                  'bg-red-500'
                                }">
                                  {Derivative.status}
                                </Badge>
                            </TableCell>
                            <TableCell>{Derivative.run_created_at}</TableCell>
                            <TableCell>{Derivative.run_completed_at ?? 'N/A'}</TableCell>
                            <TableCell>{Derivative.output_files?.length ?? 'N/A'}</TableCell>
                            <TableCell><Button on:click={() => goto(`/results?id=${Derivative._id}`)}>View Results</Button></TableCell>
                        </TableRow>
                        {/each}
                    </TableBody>
                </Table>
            </section>
        </div>
    </div>
    <div class="w-full mt-6">
        <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
            <h2 class="text-xl font-semibold mb-4 ">Utilities</h2>
            <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" on:click={downlaodEEGFIle}>Download File</button>
        </section>
    </div>
</main>

{#if showToast}
    <div 
    class="toast toast-top toast-end"
    transition:fade
    >
    <Alert class="{toastType === 'success' ? 'bg-green-300' : 'bg-red-300'} shadow-lg hover:shadow-xl">
        <span class="text-base">{toastMessage}</span>
    </Alert>
    </div>
{/if}
<!-- Have an area that shows duplicate files and participants -->