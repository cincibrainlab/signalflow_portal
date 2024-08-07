<script lang="ts">
    import type { PageData } from './$types';
    import { onMount } from 'svelte';
    import { getFile } from '$lib/services/apiService';
    import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "$lib/components/ui/table";
    import Papa from 'papaparse';
    import * as XLSX from 'xlsx';

    export let data: PageData;

    let fileRunId = data.fileRunId;
    let fileRun = data.fileRun;
    let outputFiles = data.fileRun.output_files;

    let activeTab = 0;
    const tabs = ['Details', 'Table', 'Plots', 'PDFs'];

    let loadedFiles = {};
    let csvData = [];
    let channels = [];
    let currentPage = 0;
    const ROWS_PER_PAGE = 100;

    function setActiveTab(index: number) {
        activeTab = index;
    }

    async function loadFile(filePath: string) {
        if (!loadedFiles[filePath]) {
            try {
                const response = await getFile(filePath);
                const blob = await response.blob();
                const fileExtension = getFileExtension(filePath);

                if (fileExtension === 'csv') {
                    const text = await blob.text();
                    Papa.parse(text, {
                        dynamicTyping: true,
                        complete: function(results) {
                            console.log("Parsing complete:", results);
                            channels = results.data[0].map((header, index) => 
                                index === 0 && header === null ? '' : header
                            );
                            csvData = results.data.slice(1).map(row =>
                                row.map(cell =>
                                    typeof cell === 'number' ? Number(cell.toFixed(3)) : cell
                                )
                            );
                            loadedFiles[filePath] = true;
                        },
                        error: function(error) {
                            console.error("Error parsing CSV:", error);
                        }
                    });
                } else if (['txt', 'json'].includes(fileExtension)) {
                    const text = await blob.text();
                    loadedFiles[filePath] = text;
                } else if (['xlsx', 'xls'].includes(fileExtension)) {
                    const arrayBuffer = await blob.arrayBuffer();
                    const workbook = XLSX.read(arrayBuffer, { type: 'array' });
                    const sheetName = workbook.SheetNames[0];
                    const worksheet = workbook.Sheets[sheetName];
                    loadedFiles[filePath] = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
                } else {
                    loadedFiles[filePath] = URL.createObjectURL(blob);
                }
            } catch (error) {
                console.error('Error loading file:', error);
            }
        }
    }

    function getFileExtension(filePath: string) {
        return filePath.split('.').pop().toLowerCase();
    }

    function nextPage() {
        if ((currentPage + 1) * ROWS_PER_PAGE < csvData.length) {
            currentPage++;
        }
    }

    function prevPage() {
        if (currentPage > 0) {
            currentPage--;
        }
    }

    $: tableLikeFiles = outputFiles.filter(file => ['csv', 'tsv', 'xlsx', 'xls'].includes(getFileExtension(file)));
    $: plotFiles = outputFiles.filter(file => ['png', 'jpg', 'jpeg', 'gif', 'svg'].includes(getFileExtension(file)));
    $: pdfFiles = outputFiles.filter(file => getFileExtension(file) === 'pdf');

    onMount(() => {
        // Load all files when the component mounts
        outputFiles.forEach(loadFile);
    });
</script>

<main class="container mx-auto p-4">
    <header class="text-center mb-2">
        <h1 class="text-4xl font-bold">Results Details</h1>
        <p class="text-lg">{fileRun.analysis_name}</p>
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
                <h2 class="text-2xl font-semibold mb-4">File Run Details</h2>
                {#if fileRun}
                    <Table>
                        <TableBody>
                            <TableRow>
                                <TableCell>Analysis Name</TableCell>
                                <TableCell>{fileRun.analysis_name}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Flow Name</TableCell>
                                <TableCell>{fileRun.flow_name}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>File Name</TableCell>
                                <TableCell>{fileRun.original_name}</TableCell>
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
                <h2 class="text-2xl font-semibold mb-4">Table Data</h2>
                {#if tableLikeFiles.length > 0}
                    {#each tableLikeFiles as file}
                        <h3 class="text-xl font-semibold mt-4 mb-2">{file.split('/').pop()}</h3>
                        {#if loadedFiles[file]}
                            {#if getFileExtension(file) === 'csv'}
                            <div class="flex justify-between mt-4">
                                <button on:click={prevPage} disabled={currentPage === 0}>Previous Page</button>
                                <span>Page {currentPage + 1} of {Math.ceil(csvData.length / ROWS_PER_PAGE)}</span>
                                <button on:click={nextPage} disabled={(currentPage + 1) * ROWS_PER_PAGE >= csvData.length}>Next Page</button>
                            </div>
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            {#each channels as channel, index}
                                                <TableHead>{channel}</TableHead>
                                            {/each}
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {#each csvData.slice(currentPage * ROWS_PER_PAGE, (currentPage + 1) * ROWS_PER_PAGE) as row}
                                            <TableRow>
                                                {#each row as cell, index}
                                                    <TableCell class={index === 1 ? "border-r-2 border-gray-200" : ""}>{cell}</TableCell>
                                                {/each}
                                            </TableRow>
                                        {/each}
                                    </TableBody>
                                </Table>
                                <div class="flex justify-between mt-4">
                                    <button on:click={prevPage} disabled={currentPage === 0}>Previous Page</button>
                                    <span>Page {currentPage + 1} of {Math.ceil(csvData.length / ROWS_PER_PAGE)}</span>
                                    <button on:click={nextPage} disabled={(currentPage + 1) * ROWS_PER_PAGE >= csvData.length}>Next Page</button>
                                </div>
                            {:else if ['xlsx', 'xls'].includes(getFileExtension(file))}
                                <!-- ... Excel file display logic ... -->
                            {:else}
                                <pre>{loadedFiles[file]}</pre>
                            {/if}
                        {:else}
                            <p>Loading...</p>
                        {/if}
                    {/each}
                {:else}
                    <p>No table-like files available.</p>
                {/if}
            </div>
        {:else if activeTab === 2}
            <div class="p-4">
                <h2 class="text-2xl font-semibold mb-4">Plots</h2>
                {#if plotFiles.length > 0}
                    <div class="grid grid-cols-2 gap-4">
                        {#each plotFiles as file}
                            <div>
                                <h3 class="text-xl font-semibold mb-2">{file.split('/').pop()}</h3>
                                {#if loadedFiles[file]}
                                    <img src={loadedFiles[file]} alt={file} class="max-w-full h-auto" />
                                {:else}
                                    <p>Loading...</p>
                                {/if}
                            </div>
                        {/each}
                    </div>
                {:else}
                    <p>No plot files available.</p>
                {/if}
            </div>
        {:else if activeTab === 3}
            <div class="p-4">
                <h2 class="text-2xl font-semibold mb-4">PDFs</h2>
                {#if pdfFiles.length > 0}
                    {#each pdfFiles as file}
                        <h3 class="text-xl font-semibold mt-4 mb-2">{file.split('/').pop()}</h3>
                        {#if loadedFiles[file]}
                            <PdfViewer url={loadedFiles[file]} />
                        {:else}
                            <p>Loading...</p>
                        {/if}
                    {/each}
                {:else}
                    <p>No PDF files available.</p>
                {/if}
            </div>
        {/if}
    </div>
</main>