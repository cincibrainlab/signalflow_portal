<script lang="ts">
	import { writable } from 'svelte/store';
	import { createUppyInstance } from '$lib/uppy';
	import { onMount } from 'svelte';

	type EEGFormat = {
		id: string;
		name: string;
	};

	const baseUrl = 'http://localhost:8001/api/';

	let eegFormats: EEGFormat[] = [];
	let eegParadigms: EEGFormat[] = []; // Assuming eegParadigms has a similar structure
	let eegFormat = '';
	let eegParadigm = '';
	let emailAddress = '';
	let datasetSelection = '';
	let newDatasetName = '';
	let newDatasetDescription = '';
	let datasets = writable(['Example Dataset 1', 'Example Dataset 2', 'Example Dataset 3'] ?? []);

	const createDataset = async () => {
		// Temporarily holds current datasets to avoid reactivity issues
		let currentDatasets: string[] = []; // Explicitly type as string array to avoid type 'any' issues
		datasets.subscribe((value) => {
			currentDatasets = value ?? []; // Ensure value is not undefined by providing a default empty array
		})();

		if (currentDatasets.some((dataset) => dataset === newDatasetName)) {
			alert('Dataset name already exists. Please choose a different name.');
		} else {
			// Add the new dataset name and description to the datasets store
			datasets.update((n) => [...n, `${newDatasetName}: ${newDatasetDescription}`]);
			datasetSelection = newDatasetName; // Select the newly created dataset
			alert('Dataset created successfully with description.');
		}
	};
	const saveDataset = async (
		datasetName: string,
		description: string,
		eegFormatId: string,
		eegParadigmId: string
	) => {
		console.log(`Attempting to save dataset: ${datasetName}`);
		try {
			const response = await fetch(`${baseUrl}add-dataset`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					dataset_name: datasetName,
					description: description,
					eeg_format_id: eegFormatId,
					eeg_paradigm_id: eegParadigmId
				})
			});
			const result = await response.json();
			console.log(`Response received: ${JSON.stringify(result)}`);
			if (result.success) {
				alert('Dataset created successfully.');
				console.log(`Dataset ${datasetName} created successfully.`);
				// Update local datasets array to include the new dataset
				datasets.update((n) => [...n, datasetName]);
				datasetSelection = datasetName; // Select the newly created dataset
			} else {
				alert('Failed to create dataset: ' + result.message);
				console.error('Failed to create dataset:', result.message);
			}
		} catch (error) {
			console.error('Error creating dataset:', error);
			alert('Error creating dataset. Please try again.');
		}
	};
	onMount(async () => {
		console.log('Mounting component and fetching data...');
		try {
			const uppy = createUppyInstance();
			console.log('Uppy instance created:', uppy);

			console.log('Fetching data from APIs...');
			const responses = await Promise.all([
				fetch(`${baseUrl}list-eeg-formats`).then((response) => response.json()),
				fetch(`${baseUrl}list-eeg-paradigms`).then((response) => response.json()),
				fetch(`${baseUrl}list-datasets`).then((response) => response.json())
			]);
			console.log('Data fetched from APIs:', responses);

			// Assuming the response JSON structure is known and assigning types
			const [eegFormatsResponse, eegParadigmsResponse, datasetsResponse] = responses;
			eegFormats = eegFormatsResponse;
			console.log('EEG Formats:', eegFormats);
			eegParadigms = eegParadigmsResponse;
			console.log('EEG Paradigms:', eegParadigms);
			datasets.set(datasetsResponse);
			console.log('Datasets:', $datasets);
		} catch (error) {
			console.error('Failed to load data:', error);
		}
	});
	const submitForm = async () => {
		console.log({ eegFormat, eegParadigm, emailAddress, datasetSelection, newDatasetName });
		// Implement submission logic here, potentially as a fetch POST request
	};

	const handleCreateDatasetClick = () => {
		console.log('Creating dataset with:', {
			Name: newDatasetName,
			Description: newDatasetDescription,
			EEGFormatID: eegFormat,
			EEGParadigmID: eegParadigm
		});

		// Now call the saveDataset function with the logged values
		saveDataset(newDatasetName, newDatasetDescription, eegFormat, eegParadigm);
	};
</script>

<div class="upload-form">
	<h2>SignalFlowEeg Upload Portal 6</h2>
	<div class="form-row">
		<select bind:value={eegFormat}>
			<option value="" disabled>Select EEG Format</option>
			{#each eegFormats as format}
				<option value={format.id}>{format.name}</option>
			{/each}
		</select>

		<select bind:value={eegParadigm}>
			<option value="" disabled>Select EEG Paradigm</option>
			{#each eegParadigms as paradigm}
				<option value={paradigm.id}>{paradigm.name}</option>
			{/each}
		</select>
	</div>

	<div class="form-row">
		<select bind:value={datasetSelection}>
			<option value="" disabled>Select or Create Dataset</option>
			{#each $datasets as dataset}
				<option value={dataset.id}>{dataset.name}</option>
			{/each}
			<option value="create_new">Create New Dataset</option>
		</select>
	</div>
	{#if datasetSelection === 'create_new'}
		<div class="form-row">
			<input type="text" bind:value={newDatasetName} placeholder="Enter Dataset Name" />
		</div>
		<div class="form-row">
			<textarea bind:value={newDatasetDescription} placeholder="Enter Dataset Description"
			></textarea>
		</div>
		<div class="form-row">
			<button on:click={handleCreateDatasetClick}>Create New Dataset</button>
		</div>
	{/if}

	<input type="email" bind:value={emailAddress} placeholder="Email Address" />

	<div id="uppy-dashboard-container" />

	<button on:click={submitForm}>Submit</button>
</div>

<style>
	.upload-form {
		display: flex;
		flex-direction: column;
		gap: 20px;
		max-width: 600px;
		margin: auto;
		padding: 20px;
		border: 2px solid #007bff;
		border-radius: 12px;
		background-color: #f9f9f9;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}

	h2 {
		font-family: 'Arial', sans-serif;
		font-size: 24px;
		font-weight: bold;
		color: #333;
		margin-bottom: 20px;
	}

	.form-row {
		display: flex;
		justify-content: space-between;
		gap: 10px;
	}

	input,
	select,
	textarea {
		flex: 1;
		padding: 12px;
		border: 2px solid #ccc;
		border-radius: 6px;
		font-size: 16px;
	}

	button {
		width: 100%;
		padding: 12px 20px;
		background-color: #007bff;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 16px;
		font-weight: 600;
		text-transform: uppercase;
		transition: background-color 0.3s ease;
	}

	button:hover {
		background-color: #0056b3;
	}
</style>
