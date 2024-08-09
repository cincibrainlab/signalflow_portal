<script lang="ts">
    import type { PageData } from './$types';
    import { onMount } from 'svelte';
    import { getFile } from '$lib/services/apiService';
    import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "$lib/components/ui/table";
    import { Tabs, TabsContent, TabsList, TabsTrigger } from "$lib/components/ui/tabs";
    import { Button } from "$lib/components/ui/button";
    import { Card, CardContent, CardHeader, CardTitle } from "$lib/components/ui/card";
    import Papa from 'papaparse';
    import * as XLSX from 'xlsx';

    export let data: PageData;

    let fileRunId = data.fileRunId;
    let fileRun = data.fileRun;
    let outputFiles = data.fileRun.output_files;

    let loadedFiles = {};
    let csvData = [];
    let channels = [];
    let currentPage = 0;
    const ROWS_PER_PAGE = 100;

    $: tableLikeFiles = outputFiles.filter(file => ['csv', 'tsv', 'xlsx', 'xls'].includes(getFileExtension(file)));
    $: plotFiles = outputFiles.filter(file => ['png', 'jpg', 'jpeg', 'gif', 'svg'].includes(getFileExtension(file)));
    $: pdfFiles = outputFiles.filter(file => getFileExtension(file) === 'pdf');

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

    onMount(() => {
        outputFiles.forEach(loadFile);
    });
</script>

<main class="container mx-auto p-4">
    <header class="text-center mb-2">
        <h1 class="text-4xl font-bold">Results Details</h1>
        <p class="text-lg">{fileRun.analysis_name}</p>
    </header>

    <Tabs class="w-full">
        <TabsList class="mb-4">
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="table">Table</TabsTrigger>
            <TabsTrigger value="plots">Plots</TabsTrigger>
            <TabsTrigger value="pdfs">PDFs</TabsTrigger>
        </TabsList>

        <TabsContent value="details">
            <Table>
                <TableBody>
                    <TableRow>
                        <TableCell className="font-medium">Analysis Name</TableCell>
                        <TableCell>{fileRun.analysis_name}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell className="font-medium">Flow Name</TableCell>
                        <TableCell>{fileRun.flow_name}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell className="font-medium">File Name</TableCell>
                        <TableCell>{fileRun.original_name}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell className="font-medium">Status</TableCell>
                        <TableCell>{fileRun.status}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell className="font-medium">Created At</TableCell>
                        <TableCell>{fileRun.run_created_at}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell className="font-medium">Completed At</TableCell>
                        <TableCell>{fileRun.run_completed_at || 'N/A'}</TableCell>
                    </TableRow>
                </TableBody>
            </Table>
        </TabsContent>

        <TabsContent value="table">
            {#if tableLikeFiles.length > 0}
                {#each tableLikeFiles as file}
                    <h3 class="text-xl font-semibold mt-6 mb-2">{file.split('/').pop()}</h3>
                    {#if loadedFiles[file]}
                        {#if getFileExtension(file) === 'csv'}
                            <div class="flex justify-between mt-4 mb-2">
                                <Button on:click={prevPage} disabled={currentPage === 0}>Previous Page</Button>
                                <span>Page {currentPage + 1} of {Math.ceil(csvData.length / ROWS_PER_PAGE)}</span>
                                <Button on:click={nextPage} disabled={(currentPage + 1) * ROWS_PER_PAGE >= csvData.length}>Next Page</Button>
                            </div>
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        {#each channels as channel}
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
                        {:else if ['xlsx', 'xls'].includes(getFileExtension(file))}
                            <!-- Implement Excel file display logic -->
                        {:else}
                            <pre class="bg-gray-100 p-4 rounded">{loadedFiles[file]}</pre>
                        {/if}
                    {:else}
                        <p>Loading...</p>
                    {/if}
                {/each}
            {:else}
                <p>No table-like files available.</p>
            {/if}
        </TabsContent>

        <TabsContent value="plots">
            {#if plotFiles.length > 0}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {#each plotFiles as file}
                        <Card>
                            <CardHeader>
                                <CardTitle>{file.split('/').pop()}</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {#if loadedFiles[file]}
                                    <img src={loadedFiles[file]} alt={file} class="max-w-full h-auto" />
                                {:else}
                                    <p>Loading...</p>
                                {/if}
                            </CardContent>
                        </Card>
                    {/each}
                </div>
            {:else}
                <p>No plot files available.</p>
            {/if}
        </TabsContent>

        <TabsContent value="pdfs">
            {#if pdfFiles.length > 0}
                {#each pdfFiles as file}
                    <Card class="mb-6">
                        <CardHeader>
                            <CardTitle>{file.split('/').pop()}</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {#if loadedFiles[file]}
                                <iframe src={loadedFiles[file]} width="100%" height="600px" title={file}></iframe>
                            {:else}
                                <p>Loading...</p>
                            {/if}
                        </CardContent>
                    </Card>
                {/each}
            {:else}
                <p>No PDF files available.</p>
            {/if}
        </TabsContent>
    </Tabs>
</main>