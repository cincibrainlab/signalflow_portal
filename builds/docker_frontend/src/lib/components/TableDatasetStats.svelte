<script lang="ts">
	import { onMount, createEventDispatcher } from 'svelte';
	import type { DataHandler } from '@vincjo/datatables';
	import ThSort from '$lib/components/client/ThSort.svelte';
	import ThFilter from '$lib/components/client/ThFilter.svelte';
	import Search from '$lib/components/client/Search.svelte';
	import RowsPerPage from '$lib/components/client/RowsPerPage.svelte';
	import RowCount from '$lib/components/client/RowCount.svelte';
	import Pagination from '$lib/components/client/Pagination.svelte';

	import { popup } from '@skeletonlabs/skeleton';
	import { getEEGFormats, getEEGParadigms, mergeDatasets } from '$lib/services/apiService';
	import type { DatasetRow, EEGFormat, DatasetStats } from '$lib/types';
	import { addDataset, updateDataset } from '$lib/services/apiService';

	export let handler: DataHandler<DatasetStats>;
	const dispatch = createEventDispatcher();

	let editingDataset: DatasetRow | null = null;
	let showEditPopup = false;
	let formats: EEGFormat[] = [];
	let paradigms: EEGFormat[] = [];
	let selectedDatasets: DatasetRow[] = [];

	onMount(async () => {
		const [fetchedFormats, fetchedParadigms] = await Promise.all([getEEGFormats(), getEEGParadigms()]);
		formats = fetchedFormats;
		paradigms = fetchedParadigms;
	});

	const rows = handler.getRows();

	function openEditPopup(dataset: DatasetRow) {
		editingDataset = dataset;
		showEditPopup = true;
	}

	function closeEditPopup() {
		showEditPopup = false;
		editingDataset = null;
	}

	async function saveChanges() {
		if (editingDataset !== null) {
			const response = await updateDataset(editingDataset);
			console.log('Response:', response);

			if (response.success) {
				dispatch('update', { dataset: editingDataset });
				closeEditPopup();
			} else {
				console.error('Failed to update dataset');
			}
		}
	}

	async function handleMerge() {
		console.log('Attempting to merge datasets:', $selectedMergeDataset1, $selectedMergeDataset2);
		if ($selectedMergeDataset1 && $selectedMergeDataset2) {
			const response = await mergeDatasets($selectedMergeDataset1, $selectedMergeDataset2);
			console.log('Merge response:', response);
			if (response.success) {
				dispatch('merged', { message: response.message });
				selectedMergeDataset1.set('');
				selectedMergeDataset2.set('');
			} else {
				console.error('Merge failed:', response.message);
			}
		} else {
			console.error('Select exactly two datasets to merge');
		}
	}
	function toggleDatasetSelection(dataset: DatasetRow) {
		const index = selectedDatasets.findIndex(d => d.dataset_id === dataset.dataset_id);
		if (index > -1) {
			selectedDatasets.splice(index, 1);
		} else if (selectedDatasets.length < 2) {
			selectedDatasets.push(dataset);
		} else {
			console.error('Cannot select more than two datasets for merging');
		}
	}

    import { writable } from 'svelte/store';

    const selectedMergeDataset1 = writable('');
    const selectedMergeDataset2 = writable('');
</script>
<header></header>
<div class="merge-dataset-tool" style="display: flex; flex-direction: column; align-items: center; gap: 20px; padding: 20px;">
	<h3>Merge Datasets</h3>
	<div class="dropdowns" style="width: 100%; display: flex; justify-content: space-evenly; align-items: center;">
		<div style="flex: 1; margin-right: 10px;">
			<label for="dataset1" class="label">Source Dataset:</label>
			<select id="dataset1" bind:value={$selectedMergeDataset1} class="select">
				<option value="" disabled selected>Select Dataset 1</option>
				{#each $rows as row}
				<option value={row.dataset_id}>{row.dataset_name}</option>
				{/each}
			</select>
		</div>
		<div style="flex: 1; margin-left: 10px;">
			<label for="dataset2" class="label">Target Dataset:</label>
			<select id="dataset2" bind:value={$selectedMergeDataset2} class="select">
				<option value="" disabled selected>Select Dataset 2</option>
				{#each $rows as row}
					<option value={row.dataset_id}>{row.dataset_name}</option>
				{/each}
			</select>
		</div>
		<button on:click={handleMerge} disabled={!selectedMergeDataset1 || !selectedMergeDataset2 || selectedMergeDataset1 === selectedMergeDataset2} class="btn variant-filled-primary">
			Merge →
		</button>
	</div>
</div>

<table>
	<thead>
		<tr>
			<ThSort {handler} orderBy="dataset_name">Name</ThSort>
			<ThSort {handler} orderBy="description">Description</ThSort>
			<ThSort {handler} orderBy="file_count">File Count</ThSort>
		</tr>
	</thead>
	<tbody>
		{#await $rows}
			<p>Loading...</p>
		{:then rows}
			{#each rows as row (row.dataset_id)}
				<tr on:click={() => toggleDatasetSelection(row)} class:selected={selectedDatasets.includes(row)}>
					<td>
						{#if row.dataset_id}
							{@const [datasetId, badgeColor] = row.dataset_id.split('|')}
							<span class="badge oval" style="background-color: {badgeColor};">{row.dataset_name}</span>
						{:else}
							<span class="badge oval variant-soft-primary">{row.dataset_name}</span>
						{/if}
					</td>
					<td>
						<span class="badge oval variant-soft-secondary">{row.description}</span>
					</td>
					<td>{row.file_count}</td>
				</tr>
			{/each}
		{:catch error}
			<p>Error loading data.</p>
		{/await}
	</tbody>
</table>
{#if selectedDatasets.length === 2}
	<button on:click={handleMerge} class="btn variant-filled-primary">Merge Selected Datasets</button>
{/if}
{#if showEditPopup && editingDataset}
	<div class="edit-popup card p-4 variant-filled-surface">
		<div class="form-group">
			<label for="dataset_name" class="label">Name:</label>
			<input type="text" bind:value={editingDataset.dataset_name} id="dataset_name" class="input">
		</div>

		<div class="form-group">
			<label for="description" class="label">Description:</label>
			<textarea bind:value={editingDataset.description} id="description" class="textarea"></textarea>
		</div>
		<div class="flex justify-end space-x-2 mt-4">
			<button on:click={saveChanges} class="btn variant-filled-secondary">Save Changes</button>
			<button on:click={closeEditPopup} class="btn variant-filled-tertiary">Cancel</button>
		</div>
	</div>
{/if}
<footer>
	<Pagination {handler} />
	<RowCount {handler} />
	<Search {handler} />
	<RowsPerPage {handler} />
</footer>
<style>
	header {
		padding-top: 5;
	}
	header {
		padding: 0 5;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	footer {
		border-top: 1px solid #e0e0e0;
		padding-top: 10px;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	table {
		text-align: left;
		border-collapse: separate;
		border-spacing: 0;
		width: 100%;
	}
	tbody tr:hover {
		background: 'bg-fuchsia-600';
		transition: background 0.2s;
	}
	td {
		padding: 4px 20px;
		border-bottom: 1px solid #eee;
	}
	.edit-popup {
		position: fixed;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		padding: 20px;
		border-radius: 8px;
		box-shadow: 0 4px 6px rgba(0,0,0,0.1);
		z-index: 100;
	}
	.selected {
		background-color: #f0f0f0;
	}
</style>

