<script lang="ts">
	import { createEventDispatcher, onMount, onDestroy } from 'svelte';
	import Uppy from '@uppy/core';
	import Dashboard from '@uppy/dashboard';
	import GoldenRetriever from '@uppy/golden-retriever';
	import Tus from '@uppy/tus';
	import Compressor from '@uppy/compressor';
	import DefaultStore from '@uppy/store-default';
	import Form from '@uppy/form';
	import '@uppy/core/dist/style.css';
	import '@uppy/dashboard/dist/style.css';
	import type { UploadedFile } from '$lib/types';

	import { processUploads } from '$lib/services/apiService';

	export let options = {}; // Options for configuring the Uppy instance

	const UPLOADER = 'tus';
	const TUS_ENDPOINT = "http://localhost:3001/files/";

	let uppy: Uppy;
	let dispatch = createEventDispatcher();

	onMount(() => {
		uppy = new Uppy({
			store: new DefaultStore(),
			debug: true,
			restrictions: {
				allowedFileTypes: ['.set', '.fdt', '.fif']
			},
			...options
		})
			.use(Dashboard, {
				inline: true,
				target: '#uppy-dashboard-container',
				showProgressDetails: true,
				proudlyDisplayPoweredByUppy: true,
				hideUploadButton: true,
				height: 400
			})
			.use(Compressor)
			.use(Tus, { endpoint: TUS_ENDPOINT, limit: 6 })
			.use(Form, {
				target: '#upload_form',
				resultName: 'uppyResult',
				getMetaFromForm: true,
				addResultToForm: true,
				submitOnSuccess: false,
				triggerUploadOnSubmit: false
			})
			.use(GoldenRetriever, { serviceWorker: true });
		
			if ('serviceWorker' in navigator) {
				navigator.serviceWorker
					.register('/sw.js') // path to your bundled service worker with GoldenRetriever service worker
					.then((registration) => {
						console.log(
							'ServiceWorker registration successful with scope: ',
							registration.scope,
						);
					})
					.catch((error) => {
						console.log(`Registration failed with ${error}`);
					});
			}

		uppy.on('complete', (result) => {
			if (result.successful.length > 0) {
				dispatch('upload-success', result.successful);
			} else {
				dispatch('upload-failed', result.failed);
			}
		});

		uppy.setState({ files: [] });
	});

	
	export async function startUpload() {
		await uppy.upload().then(processUploads);
	}

	export function handleUploadResult(files: UploadedFile[], isSuccess: boolean): string {
		if (isSuccess) {
			return `Success: ${files.length} files uploaded.`;
		} else {
			return `Failed: No files uploaded.`;
		}
	}
</script>

<div id="uppy-dashboard-container" class="flex justify-center"></div>

<style>
	/* Add any necessary styles for the Uppy dashboard container */
	
</style>
