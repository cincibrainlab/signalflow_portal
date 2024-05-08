<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { DataHandler } from '@vincjo/datatables';
    import { Tab, TabGroup } from '@skeletonlabs/skeleton';
    import { writable } from 'svelte/store';

    import { getUploadCatalog, getImportCatalog, getDatasetCatalog, getDatasetStats } from '$lib/services/apiService';
    
    import TableUploadCatalog from '$lib/components/TableUploadCatalog.svelte';
    import TableImportCatalog from '$lib/components/TableImportCatalog.svelte';
    import TableDatasetCatalog from '$lib/components/TableDatasetCatalog.svelte';
    import TableDatasetStats from '$lib/components/TableDatasetStats.svelte';

    import type { UploadRow, ImportRow, DatasetRow, DatasetStats } from '$lib/types';
    
    let catalogTab = 'upload';
	const activeTab = writable('upload');

    const uploadHandler = new DataHandler<UploadRow>([], { rowsPerPage: 10 });
    const importHandler = new DataHandler<ImportRow>([], { rowsPerPage: 10 });
    const datasetHandler = new DataHandler<DatasetRow>([], { rowsPerPage: 10 });
    const datasetStatsHandler = new DataHandler<DatasetStats>([], { rowsPerPage: 10 });

    export async function fetchCatalogData() {
        const uploadData = await getUploadCatalog();
        console.log('Upload data2:', uploadData);
        const importData = await getImportCatalog();
        console.log('Import data2:', importData);
        uploadHandler.setRows(uploadData);
        importHandler.setRows(importData);

        const datasetData = await getDatasetCatalog();
        console.log('Dataset data:', datasetData);
        datasetHandler.setRows(datasetData);

        const datasetStatsData = await getDatasetStats();
        console.log('Dataset stats data:', datasetStatsData);
        datasetStatsHandler.setRows(datasetStatsData);
    }

    
    onMount(() => {
        fetchCatalogData();
        console.log('Fetching catalog data...', activeTab);
    });

    $: if (catalogTab === 'upload') {
        console.log('Fetching upload catalog data...');
    } else if (catalogTab === 'import') {
        console.log('Fetching import catalog data...');
    }

</script>

<TabGroup>
    <Tab bind:group={catalogTab} name="upload" value="upload">Upload Catalog</Tab>
    <Tab bind:group={catalogTab} name="import" value="import">Import Catalog</Tab>
    <Tab bind:group={catalogTab} name="dataset" value="dataset">Dataset Catalog</Tab>
    <Tab bind:group={catalogTab} name="dataset-stats" value="dataset-stats">Dataset Stats</Tab>
    <svelte:fragment slot="panel">
        {#if catalogTab === 'upload'}
            <div class="tab-content" class:active={catalogTab === 'upload'}>
                <TableUploadCatalog handler={uploadHandler} />
            </div>
        {:else if catalogTab === 'import'}
            <div class="tab-content" class:active={catalogTab === 'import'}>
                <TableImportCatalog handler={importHandler} /> 
            </div>
        {:else if catalogTab === 'dataset'}
            <div class="tab-content" class:active={catalogTab === 'dataset'}>
                <TableDatasetCatalog handler={datasetHandler} />
            </div>
        {:else if catalogTab === 'dataset-stats'}
            <div class="tab-content" class:active={catalogTab === 'dataset-stats'}>
                <TableDatasetStats handler={datasetStatsHandler} />
            </div>
        {/if}
    </svelte:fragment>
</TabGroup>
