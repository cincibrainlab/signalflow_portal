<script lang="ts">
    import { DataHandler }  from '@vincjo/datatables'

            // Define the interface for the row data
    interface UploadRow {
        upload_id: string;
        fdt_upload_id: string;
        original_name: string;
        is_set_file: boolean;
        has_fdt_file: boolean;
        fdt_filename: string;
    }
    //const handler = new DataHandler([], { rowsPerPage: 10 });
    const handler = new DataHandler<UploadRow>([], { rowsPerPage: 10 });



        // Use the interface with DataHandler


    import { onMount } from 'svelte';
    export let upload_apiUrl: string = 'http://localhost:3005/api/get-upload-catalog';
    let uploadCatalog: UploadRow[] = [];
    
    async function fetchUploadCatalog() {
        const response = await fetch(upload_apiUrl);
        uploadCatalog = await response.json();
        handler.setRows(uploadCatalog);
    }

    const rows = handler.getRows();

    onMount(() => {
        fetchUploadCatalog();
    });


</script>
<table>
    <thead>
        <tr>
            <th>Upload ID</th>
            <th>FDT Upload ID</th>
            <th>Original Name</th>
            <th>Is Set File</th>
            <th>Has FDT File</th>
            <th>FDT Filename</th>
        </tr>
    </thead>
    <tbody>
        {#await $rows}
            <p>Loading...</p>
        {:then rows}
            {#each rows as row}
                <tr>
                    <td>{row.upload_id}</td>
                    <td>{row.fdt_upload_id}</td>
                    <td>{row.original_name}</td>
                    <td>{row.is_set_file}</td>
                    <td>{row.has_fdt_file}</td>
                    <td>{row.fdt_filename}</td>
                </tr>
            {/each}
        {:catch error}
            <p>Error loading data.</p>
        {/await}
    </tbody>
</table>

<style>
    table {
        text-align: left;
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
    }
    td, th {
        padding: 4px 20px;
        border-bottom: 1px solid #eee;
    }
</style>
