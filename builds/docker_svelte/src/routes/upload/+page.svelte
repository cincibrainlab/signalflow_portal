<script lang="ts">
	import { writable } from 'svelte/store';
	import { onMount } from 'svelte';
	import { createUppyInstance } from '$lib/uppy';
	import Uppy from '@uppy/core';

	import '$lib/global.css';

	type EEGFormat = {
		id: string;
		name: string;
	};

	const baseUrl = import.meta.env.VITE_API_BASE_URL;

	let eegFormats: EEGFormat[] = [];
	let eegParadigms: EEGFormat[] = [];
	let eegFormat: string = '';
	let eegParadigm: string = '';
	let emails: string[] = [];
	let emailSelection: string = '';
	let newEmailAddress: string = '';
	let uppy = writable<Uppy | null>(null); // Initialize with a type that can be null or an Uppy instance
	
	onMount(async () => {
            uppy.set(createUppyInstance());
				console.log('Uppy instance created:', $uppy);

		const responses = await Promise.all([
			fetch(`${baseUrl}list-eeg-formats`).then((response) => response.json()),
			fetch(`${baseUrl}list-eeg-paradigms`).then((response) => response.json()),
			fetch(`${baseUrl}list-emails`).then((response) => response.json())
		]);

		const [eegFormatsResponse, eegParadigmsResponse, emailsResponse] = responses;
		eegFormats = eegFormatsResponse;
		eegParadigms = eegParadigmsResponse;
		emails = emailsResponse;

		if (eegFormats.length > 0) {
			eegFormat = eegFormats[0].id;
		}
		if (eegParadigms.length > 0) {
			eegParadigm = eegParadigms[0].id;
		}
	});
	async function submitForm(): Promise<void> {
		try {
			$uppy.upload()
				.then((result) => {
					if (result.successful.length > 0) {
						console.log(
							'Files uploaded successfully:',
							result.successful.map((file) => file.name)
						);
						displayStatusMessage('Files uploaded successfully!');
					} else {
						console.error('Upload failed:', result.failed);
						displayStatusMessage(
							'Some files failed to upload. Check the console for more details.'
						);
					}
				})
				.catch((error: Error) => {
					console.error('Error during file upload:', error);
					displayStatusMessage('Error during file upload. Please try again.');
				});
		} catch (error) {
			console.error('Error during file upload:', error);
			displayStatusMessage('Error during file upload. Please try again.');
		}
	}

	function displayStatusMessage(message: string) {
		const statusDiv = document.querySelector('.status-message');
		if (statusDiv) {
			statusDiv.innerHTML = message;
			statusDiv.style.display = 'block';
		}
	}

   // Imports and existing setup remain unchanged
   let activeTab: string = 'upload';

   $: if (activeTab === 'upload' && $uppy === null) {
       // uppy.set(createUppyInstance());
    }

	// Function to change the active tab
	function switchTab(tabName: string) {
		activeTab = tabName;
	}

</script>
<div class="max-w-4xl mx-auto px-4 py-6">
    <ul class="flex border-b bg-gray-100 rounded-lg shadow">
        <li class="{activeTab === 'upload' ? 'border-b-2 border-blue-500' : ''} mr-1">
            <button
                class:active={activeTab === 'upload'}
                on:click={() => switchTab('upload')}
                class="inline-block py-3 px-6 text-blue-500 hover:text-blue-800 font-semibold focus:outline-none"
            >Upload Portal</button>
        </li>
        <li class="{activeTab === 'jobs' ? 'border-b-2 border-blue-500' : ''} mr-1">
            <button
                class:active={activeTab === 'jobs'}
                on:click={() => switchTab('jobs')}
                class="inline-block py-3 px-6 text-blue-500 hover:text-blue-800 font-semibold focus:outline-none"
            >Job List</button>
        </li>
    </ul>
    <div class="tab-content bg-gray p-0 rounded-lg shadow-lg">
        {#if activeTab === 'upload'}
            <!-- Upload Tab Content -->
			<div class="max-w-4xl mx-auto px-4 py-0" style:hidden={activeTab !== 'upload'}>
				<div class="bg-white shadow-lg rounded-lg p-6">
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
						<div class="card bg-gray-100 p-4 rounded-lg shadow">
							<label for="eegFormat" class="font-semibold text-gray-700">EEG Format</label>
							<select id="eegFormat" bind:value={eegFormat} class="mt-1 w-full p-2 border border-gray-300 rounded">
								{#each eegFormats as format}
									<option value={format.name}>{format.name}</option>
								{/each}
							</select>
						</div>
						<div class="card bg-gray-100 p-4 rounded-lg shadow">
							<label for="eegParadigm" class="font-semibold text-gray-700">Analysis Bundle</label>
							<select id="eegParadigm" bind:value={eegParadigm} class="mt-1 w-full p-2 border border-gray-300 rounded">
								{#each eegParadigms as paradigm}
									<option value={paradigm.name}>{paradigm.name}</option>
								{/each}
							</select>
						</div>
					</div>
					<div class="card bg-gray-100 p-4 rounded-lg shadow mb-6">
						<label for="emailSelection" class="font-semibold text-gray-700">Notification Email</label>
						<div class="mt-1">
							<select id="emailSelection" bind:value={emailSelection} class="w-full p-2 border border-gray-300 rounded">
								<option value="" disabled>Select Email</option>
								{#each emails as email}
									<option value={email}>{email}</option>
								{/each}
								<option value="enter_new">Use Guest Email</option>
							</select>
						</div>
						{#if emailSelection === 'enter_new'}
							<div class="flex items-center space-x-4 mt-4">
								<input
									type="email"
									bind:value={newEmailAddress}
									placeholder="Email Address"
									class="flex-grow p-2 border border-gray-300 rounded"
								/>
								<button on:click={() => (emailSelection = newEmailAddress)} class="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
									>Use This Email</button
								>
							</div>
						{/if}
					</div>
					<div id="uppy-dashboard-container" class="p-4 bg-gray-100 rounded-lg shadow"></div>
					<div class="hidden text-red-600 font-bold p-3 border border-red-600 rounded mt-4"></div>
					<button on:click={submitForm} class="w-full py-3 mt-6 bg-blue-500 text-white rounded uppercase font-semibold tracking-wide hover:bg-blue-600 transition duration-300 ease-in-out">Submit Job</button>
				</div>
			</div>
        {/if}
        {#if activeTab === 'jobs'}
            <!-- Job List Tab Content -->
            <div>
                <h3 class="text-lg font-bold text-gray-800">Job List</h3>
                <!-- Content to display job list -->
            </div>
        {/if}
    </div>
</div>
