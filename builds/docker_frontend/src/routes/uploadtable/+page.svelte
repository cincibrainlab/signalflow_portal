<!-- <script lang="ts">
    import { onMount } from 'svelte/store';
    import type { ImportCatalogEntry } from '$lib/types'; // Assuming you have a type definition for the catalog entries

    export let apiUrl: string = 'http://localhost:3005/api/get-import-catalog';
    let importCatalog: ImportCatalogEntry[] = [];
    
    onMount(async () => {
        const response = await fetch(apiUrl);
        importCatalog = await response.json();
    });
</script>

<table>
    <thead>
        <tr>
            <th>Upload ID</th>
            <th>Original Name</th>
            <th>Is Set File</th>
            <th>Has FDT File</th>
            <th>FDT Filename</th>
        </tr>
    </thead>
    <tbody>
        {#each importCatalog as upload}
            <tr>
                <td>{upload.upload_id}</td>
                <td>{upload.original_name}</td>
                <td>{upload.is_set_file}</td>
                <td>{upload.has_fdt_file}</td>
                <td>{upload.fdt_filename}</td>
            </tr>
        {/each}
    </tbody>
</table> -->