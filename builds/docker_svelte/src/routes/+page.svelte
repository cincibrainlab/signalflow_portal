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
    let eegParadigms: EEGFormat[] = [];
    let eegFormat = '';
    let eegParadigm = '';
    let emails = '';
    let emailSelection = '';
    let newEmailAddress = '';
    let uppy;

    onMount(async () => {
        uppy = createUppyInstance();
        console.log('Uppy instance created:', uppy);

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

    const submitForm = async () => {
        uppy.upload().then(result => {
            if (result.successful.length > 0) {
                console.log('Files uploaded successfully:', result.successful.map(file => file.name));
                alert('Files uploaded successfully.');
            } else {
                console.error('Upload failed:', result.failed);
                alert('Some files failed to upload. Check the console for more details.');
            }
        }).catch(error => {
            console.error('Error during file upload:', error);
            alert('Error during file upload. Please try again.');
        });
    };
</script>

<div class="upload-form">
    <h2>SignalFlowEeg Upload Portal</h2>
    <div class="form-row">
        <select bind:value={eegFormat}>
            {#if eegFormats.length > 0}
                {#each eegFormats as format}
                    <option value={format.name}>{format.name}</option>
                {/each}
            {:else}
                <option value="" disabled>Select EEG Format</option>
            {/if}
        </select>

        <select bind:value={eegParadigm}>
            {#if eegParadigms.length > 0}
                {#each eegParadigms as paradigm}
                    <option value={paradigm.name}>{paradigm.name}</option>
                {/each}
            {:else}
                <option value="" disabled>Select EEG Paradigm</option>
            {/if}
        </select>
    </div>

    <div class="form-row">
        <select bind:value={emailSelection}>
            <option value="" disabled>Select Email</option>
            {#each emails as email}
                <option value={email.name}>{email.name}</option>
            {/each}
            <option value="enter_new">Use Guest Email</option>
        </select>
    </div>
    {#if emailSelection === 'enter_new'}
        <div class="form-row">
            <input
                type="email"
                bind:value={newEmailAddress}
                placeholder="Email Address"
                style="flex: 3;"
            />
            <button on:click={() => (emailSelection = newEmailAddress)} style="flex: 1;"
                >Use This Email</button
            >
        </div>
    {/if}
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
