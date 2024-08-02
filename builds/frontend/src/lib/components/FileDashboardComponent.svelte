<!-- src/lib/components/FileDashboardComponent.svelte -->
<script lang="ts">
    // Import necessary components and data

    import { onMount, onDestroy } from 'svelte';
    import { getOriginalFileFromUploadID, getParticipant, getEEGData, downloadFile} from '$lib/services/apiService';
    import * as d3 from 'd3';
	import { Button } from './ui/button';
    import { ArrowBigLeft, ArrowBigRight, ArrowBigLeftDash, ArrowBigRightDash } from 'lucide-svelte';

    export let data;
    let upload_id: string = data.upload_id;
    let File: any = [];
    let Participant: any = [];

    let EEGData: Float64Array[] = [];
    let numChannels: number = 0;

    let svgElement: SVGSVGElement;
    let width: number;
    let height: number;
    let xScale: d3.ScaleLinear<number, number>;
    let yScale: d3.ScaleLinear<number, number>;
    let xAxis: d3.Selection<SVGGElement, unknown, null, undefined>;
    let zoom: d3.ZoomBehavior<Element, unknown>;
    let chartArea: d3.Selection<SVGGElement, unknown, null, undefined>;

    let yScaleRange = 100; // Default y-scale range in microvolts
    let samplingRate = 100; // Default sampling rate
    let numSecondsToDisplay = 5;
    let viewportStart = 0;
    let viewportEnd = numSecondsToDisplay * samplingRate; // Initial viewport size (numSecondsToDisplay seconds * samplingRate Hz = ? samples)
    

    let resizeObserver: ResizeObserver;

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
            
            getEEGData(upload_id, samplingRate).then((response) => {
                EEGData = Array.isArray(response.data) ? response.data.map((arr: any[]) => new Float64Array(arr)) : [response ?? []] as Float64Array[];
                numChannels = response.num_channels;
                console.log('EEGData', EEGData);
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
        
        if (svgElement) {
            while (svgElement.firstChild) {
                svgElement.removeChild(svgElement.firstChild);
            }
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

        const channelHeight = height / EEGData.length;

        const clipPath = svg.append("defs").append("clipPath")
            .attr("id", "clip")
            .append("rect")
            .attr("width", width)
            .attr("height", height);

        chartArea = svg.append("g")
            .attr("clip-path", "url(#clip)");

        EEGData.forEach((channel, i) => {
            const yOffset = i * channelHeight;

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
        });

        xAxis = svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale).tickFormat(d => `${Number(d).toFixed(2)}s`));

        svg.append("g")
            .attr("class", "y-axis")
            .call(d3.axisLeft(yScale));

        // zoom = d3.zoom()
        //     .scaleExtent([1, 20])
        //     .translateExtent([[0, 0], [width, height]])
        //     .extent([[0, 0], [width, height]])
        //     .on("zoom", zoomed);

        // svg.call(zoom);
    }

    // function zoomed(event: d3.D3ZoomEvent<SVGSVGElement, unknown>) {
    //     const newXScale = event.transform.rescaleX(xScale);
    //     xAxis.call(d3.axisBottom(newXScale).tickFormat(d => `${d.toFixed(2)}s`));

    //     chartArea.selectAll("path")
    //         .attr("d", (d, i) => {
    //             const yOffset = i * (height / EEGData.length);
    //             return d3.line<number>()
    //                 .x((d, i) => newXScale((viewportStart + i) / samplingRate))
    //                 .y(d => yOffset + (height / EEGData.length) / 2 + (yScale(d) - yScale(0)) / EEGData.length)(d as number[]);
    //         });

    // }

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
        const channelHeight = height / EEGData.length;

        chartArea.selectAll("path")
            .data(EEGData)
            .attr("d", (channel, i) => {
                const yOffset = i * channelHeight;
                return d3.line<number>()
                    .x((d, i) => xScale((viewportStart + i) / samplingRate))
                    .y(d => yOffset + channelHeight / 2 + (yScale(d) - yScale(0)) / EEGData.length)(channel.slice(viewportStart, viewportEnd));
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

    function updateSamplingRate(newRate: number) {
        samplingRate = newRate;
        viewportEnd = viewportStart + numSecondsToDisplay * samplingRate;
        getEEGData(upload_id, samplingRate).then((response) => {
            EEGData = Array.isArray(response.data) ? response.data.map((arr: any[]) => new Float64Array(arr)) : [response ?? []] as Float64Array[];
            numChannels = response.num_channels;
            console.log('EEGData', EEGData);
            drawEEGPlot();
            updateYScale(yScaleRange);
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

</script>

<main class="w-11/12 mx-auto p-6 min-h-screen">
    <header class="text-center mb-8">
        <h1 class="text-4xl font-bold "> File Dashboard</h1>
        <h2 class="text-xl font-semibold ">Filename: {File.original_name}</h2>
    </header>
    <div class="flex flex-col gap-6">
        <div class="w-full">
            <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
                <div class="w-full overflow-x-scroll overflow-y-scroll border border-black">
                    <div class="w-full h-[500px]">
                        <svg bind:this={svgElement} width="100%" height="100%"></svg>
                    </div>
                </div>
                <div class="flex justify-between mt-4">
                    <div class="flex gap-2">
                        <label for="scaleInput" class="block text-base font-medium text-gray-700">Scale (µV):</label>
                        <input type="number" id="scaleInput" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" bind:value={yScaleRange} 
                        on:input={() => updateYScale(yScaleRange)}>
                    </div>
                    
                    <div class="flex gap-2">
                        <label for="numSecondsInput" class="block text
                        -base font-medium text-gray-700">Seconds to Display:</label>
                        <input type="number" id="numSecondsInput" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" bind:value={numSecondsToDisplay}
                        on:input={() => updateNumSecondsToDisplay(numSecondsToDisplay)}>
                    </div>
                    <div class="flex justify-center gap-2 mt-4">
                        <Button on:click={() => navigateViewport(-10)}><ArrowBigLeftDash/>10s</Button>
                        <Button on:click={() => navigateViewport(-1)}><ArrowBigLeft/>1s</Button>
                        <Button on:click={() => navigateViewport(1)}>1s<ArrowBigRight/></Button>
                        <Button on:click={() => navigateViewport(10)}>10s<ArrowBigRightDash/></Button>
                    </div>
                </div>
                <div class="flex gap-2 mt-4">
                    <Button on:click={() => updateYScale(50)}>50 µV</Button>
                    <Button on:click={() => updateYScale(100)}>100 µV</Button>
                    <Button on:click={() => updateYScale(200)}>200 µV</Button>
                </div>
                <header class="text-center mt-8">
                    <h2 class="text-xl font-semibold ">Advanced Settings</h2>
                </header>
                <div class="flex gap-2">
                    <label for="samplingRateInput" class="block text-base font-medium text-gray-700">Sampling Rate (Hz):</label>
                    <input type="number" id="samplingRateInput" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" bind:value={samplingRate} 
                    on:input={() => updateSamplingRate(samplingRate)}>
                </div>

            </section>
        </div>
        <div class="w-full">
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
        <section class="dark:bg-white dark:text-black rounded-xl shadow-md p-6 transition duration-300 ease-in-out hover:shadow-lg">
            <h2 class="text-xl font-semibold mb-4 ">Utilities</h2>
            <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" on:click={downlaodEEGFIle}>Download File</button>
        </section>
    </div>
</main>

  
<!-- Have an area that shows duplicate files and participants -->