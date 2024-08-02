<script lang="ts">
	import { onMount } from 'svelte';
	import UppyDashboard from '$lib/components/UppyDashboard.svelte';
	import { getToastStore } from '@skeletonlabs/skeleton';
	import { v4 as uuidv4 } from 'uuid';
	import { uniqueNamesGenerator, adjectives, animals } from 'unique-names-generator';
	import type { Config } from 'unique-names-generator';

	let uppyDashboardComponent: UppyDashboard;
	const toastStore = getToastStore();

	function triggerToast(message: string) {
		toastStore.trigger({
			message: message,
			timeout: 3000
		});
	}

	function uuidToColor(uuid: any) {
		let hash = 0;
		for (let i = 0; i < uuid.length; i++) {
			hash = uuid.charCodeAt(i) + ((hash << 5) - hash);
		}
		let color = '#';
		for (let i = 0; i < 3; i++) {
			let value = (hash >> (i * 8)) & 0xff;
			// Ensure the color is lighter by adding a base value, e.g., 127 (half of 255)
			value = (value + 200) >> 1; // This ensures that the value is always above 127
			color += ('00' + value.toString(16)).substr(-2);
		}
		return color;
	}
	
	function generateDatasetName() {
		const config: Config = {
			dictionaries: [adjectives, animals],
			separator: '-',
			style: 'lowerCase'
		};
		console.log(uniqueNamesGenerator(config));

		return uniqueNamesGenerator(config); // Generates names like "happy-elephant"
	}

	async function submitForm(): Promise<void> {
		const datasetId = uuidv4()
		const datasetName = generateDatasetName();
		// Add hidden fields to the form, removing existing ones first
		let existingDatasetIdField = document.querySelector('input[name="datasetId"]');
		if (existingDatasetIdField) {
			existingDatasetIdField.remove();
		}
		const hiddenDatasetIdField = document.createElement('input');
		hiddenDatasetIdField.type = 'hidden';
		hiddenDatasetIdField.name = 'datasetId';
		let badgeColor = uuidToColor(datasetId);
		hiddenDatasetIdField.value = datasetId + '|' + badgeColor;
		document.getElementById('upload_form')?.appendChild(hiddenDatasetIdField);

		let existingDatasetNameField = document.querySelector('input[name="datasetName"]');
		if (existingDatasetNameField) {
			existingDatasetNameField.remove();
		}
		const hiddenDatasetNameField = document.createElement('input');
		hiddenDatasetNameField.type = 'hidden';
		hiddenDatasetNameField.name = 'datasetName';
		hiddenDatasetNameField.value = datasetName;
		document.getElementById('upload_form')?.appendChild(hiddenDatasetNameField);
		if (uppyDashboardComponent) {
			await uppyDashboardComponent.startUpload();
		}
	}
</script>

<div class="container mx-auto p-4 max-w-2xl">
	<h1 class="text-2xl font-bold mb-4">Upload Your Session Files</h1>
	<p class="mb-4">Drag and drop your files or click to browse. Once you've selected your files, click "Submit Job" to start the upload.</p>
	
	<form id="upload_form" on:submit|preventDefault={submitForm}>
		<UppyDashboard
			bind:this={uppyDashboardComponent}
			on:upload-success={(event) => {
				const message = uppyDashboardComponent.handleUploadResult(event.detail, true);
				triggerToast(message);
			}}
			on:upload-failed={(event) => {
				const message = uppyDashboardComponent.handleUploadResult(event.detail, false);
				triggerToast(message);
			}}
		/>
		<div class="mt-4 flex justify-center">
			<button type="submit" class="btn variant-filled-primary font-bold py-2 px-4 rounded">Submit Job</button>
		</div>
	</form>
</div>

<style>
	/* Add any custom styles here */
</style>