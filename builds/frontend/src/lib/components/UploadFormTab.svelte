<script lang="ts">
	import { onMount } from 'svelte';
	import UppyDashboard from '$lib/components/UppyDashboard.svelte';
	import { getToastStore } from '@skeletonlabs/skeleton';
	import { getEEGFormats, getEEGParadigms, getEmails } from '$lib/services/apiService';
	import type { EEGFormat } from '$lib/types';
	

	let activeTab: string = 'upload';

	const toastStore = getToastStore();
	let uppyDashboardComponent: UppyDashboard;

	let eegFormats: EEGFormat[] = [],
		eegParadigms: EEGFormat[] = [],
		emails: EEGFormat[] = [];

	let eegFormat: string | null = null,
		eegParadigm: string | null = null,
		emailSelection: string | null = null;

	let newEmailAddress: string = '';

	function validateEmail(emailSelection: string | null, newEmailAddress: string | null) {
		return !emailSelection || (emailSelection === 'enter_new' && !newEmailAddress)
			? 'Please select an email address before submitting.'
			: null;
	}

	function validateEEGFormat(eegFormat: string | null) {
		return !eegFormat ? 'Please select an EEG format before submitting.' : null;
	}

	function validateEEGParadigm(eegParadigm: string | null) {
		return !eegParadigm ? 'Please select an EEG paradigm before submitting.' : null;
	}

	import { uniqueNamesGenerator, adjectives, animals } from 'unique-names-generator';
	import type { Config } from 'unique-names-generator'

	function generateDatasetName() {
		const config: Config = {
			dictionaries: [adjectives, animals],
			separator: '-',
			style: 'lowerCase'
		};
		console.log(uniqueNamesGenerator(config));

		return uniqueNamesGenerator(config); // Generates names like "happy-elephant"
	}

	import { v4 as uuidv4 } from 'uuid';

	function generateDatasetId() {
		return uuidv4();
	}

	async function submitForm(): Promise<void> {
		// Consolidated validation checks for email, EEG format, and EEG paradigm using imported functions
		const validationErrors = [
			{
				condition: validateEmail(emailSelection, newEmailAddress),
				message: 'Please select an email address before submitting.'
			},
			{
				condition: validateEEGFormat(eegFormat),
				message: 'Please select an EEG format before submitting.'
			},
			{
				condition: validateEEGParadigm(eegParadigm),
				message: 'Please select an EEG paradigm before submitting.'
			}
		].filter((error) => error !== null);

		const firstError = validationErrors.find((error) => error.condition);

		if (firstError) {
			console.error('Validation error:', firstError.message);
			triggerToast(firstError.message);
			return; // Stop the function from proceeding further
		} else {
			console.log('Submitting form...');

			// Generate new dataset ID and name
			const datasetId = generateDatasetId();
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
	}

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



	onMount(async () => {
		//uppy = createUppyInstance();
		const responses = await Promise.all([getEEGFormats(), getEEGParadigms(), getEmails()]);
		[eegFormats, eegParadigms, emails] = responses;
		eegFormat = eegParadigm = null; // Reset both to null
	});
</script>

<!-- Upload Tab Content -->
<form id="upload_form" on:submit|preventDefault={submitForm}>
	<div class="p-2 shadow-md rounded-lg">
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<div class="card p-4 rounded-lg">
				<label for="eegFormat" class="label mb-2">
					<span class="label-text font-semibold">EEG Format</span>
				</label>
				<select
					id="eegFormat"
					size="6"
					bind:value={eegFormat}
					class="select select-bordered w-full h-48 custom-select"
				>
					<option value={null} disabled selected>Select EEG Format</option>
					{#each eegFormats as format}
						<option value={format.name}>{format.description}</option>
					{/each}
				</select>
			</div>
			<div class="card p-4 rounded-lg">
				<label for="eegParadigm" class="label mb-2">
					<span class="label-text font-semibold">Analysis Bundle</span>
				</label>
				<select
					id="eegParadigm"
					size="6"
					bind:value={eegParadigm}
					class="select select-bordered w-full h-48 custom-select"
				>
					<option value={null} disabled selected>Select Analysis Bundle</option>
					{#each eegParadigms as paradigm}
						<option value={paradigm.name}>{paradigm.name}</option>
					{/each}
				</select>
			</div>
		</div>
		<div class="card p-2 rounded-lg mt-4">
			<label for="emailSelection" class="label">
				<span class="label-text font-semibold">Notification Email</span>
			</label>
			<div>
				<select
					id="emailSelection"
					bind:value={emailSelection}
					class="select select-bordered w-full custom-select"
				>
					<option value={null} disabled selected>Select Email</option>
					{#each emails as email}
						<option value={email.name}>{email.name}</option>
					{/each}
					<option value="enter_new">Use Guest Email</option>
				</select>
			</div>
			{#if emailSelection === 'enter_new'}
				<div class="mt-4">
					<input
						type="email"
						bind:value={newEmailAddress}
						placeholder="Email Address"
						class="input input-bordered w-full"
					/>
					<button
						on:click={() => (emailSelection = newEmailAddress)}
						class="btn btn-primary mt-2">Use This Email</button
					>
				</div>
			{/if}
			<input type="hidden" name="datasetName" value="" />
			<input type="hidden" name="datasetId" value="" />
			<br>
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
				<button type="submit" class="btn variant-filled-primary font-bold py-2 px-4 rounded"
					>Submit Job</button
				>
			</div>
		</div>
	</div>
</form>

<style>
	.custom-select {
		border-radius: 0.5rem;
		padding: 0.5rem;
	}

	.custom-select option {
		padding: 0.5rem;
		border-radius: 0.25rem;
		margin: 0.25rem 0;
		transition: background-color 0.2s ease;
	}

	.custom-select option:checked,
	.custom-select option:hover {
		background-color: rgba(59, 130, 246, 0.1);
		color: #3b82f6;
	}

	.custom-select:focus {
		outline: none;
		box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
	}
</style>