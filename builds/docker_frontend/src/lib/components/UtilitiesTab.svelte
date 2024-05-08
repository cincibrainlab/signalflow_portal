<script lang="ts">
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';

	import { callAPI } from '$lib/services/apiService';
	import type { DBStats, PortalPaths } from '$lib/types';
	let dbstats: DBStats = JSON.parse('{}') as DBStats;
	let portalPaths: PortalPaths = JSON.parse('{}') as PortalPaths;

	//let activeTab: string = 'utilities';

	async function loadDbStats(): Promise<DBStats> {
		try {
			const response: string = await callAPI('load-database-summary');
			dbstats = JSON.parse(response) as DBStats;
			console.log('Data loaded successfully:', dbstats);
			return dbstats;
		} catch (error: any) {
			console.error('Failed to load data:', error);
			dbstats = JSON.parse('{}') as DBStats;
			return dbstats;
		}
	}

	async function loadPaths(): Promise<PortalPaths> {
		try {
			const response: string = await callAPI('get-portal-paths');
			portalPaths = JSON.parse(response);
			console.log('Paths loaded successfully:', portalPaths);
			return portalPaths;
		} catch (error: any) {
			console.error('Failed to load paths:', error);
			portalPaths = {};
			return portalPaths;
		}
	}

	let isMounted: boolean = false;
	onMount(async () => {
		isMounted = true;

		const pathsResponse = await callAPI('get-portal-paths');
		portalPaths = JSON.parse(pathsResponse);

		const dbstatsResponse: string = await callAPI('load-database-summary');
		dbstats = JSON.parse(dbstatsResponse) as DBStats;
	});

	export let utilitytab_statusText: string = 'No status message available.';
	export function updateUtilityStatusText(newStatus: string): void {
		utilitytab_statusText = newStatus;
		console.log(`Status updated to: ${newStatus}`);
	}

	$: if (utilitytab_statusText) {
		(async () => {
			if (isMounted) {
				dbstats = await loadDbStats();
				portalPaths = await loadPaths();
			}
		})();
	}

	const activeTab = writable('utilities');
</script>

<div class="flex justify-center">
	<div class="md:w-3/4 p-4">
		<div class="card variant-glass p-4 mb-4">
			<h2 class="text-lg font-semibold mb-2">Status View</h2>
			<textarea
				class="text-gray-600 w-full p-2 border border-gray-300 rounded"
				readonly
				style="height: 150px;">{utilitytab_statusText}</textarea
			>
		</div>
		<div class="card variant-glass p-4 mb-4">
			<h2 class="text-lg font-semibold mb-2">Buttons</h2>
			<div class="flex flex-wrap justify-center space-x-2">
				<button
					class="btn variant-filled-primary"
					on:click={async () => {
						utilitytab_statusText = await callAPI('test');
					}}>Test API</button
				>
				<button
					class="btn variant-filled-primary"
					on:click={async () => {
						utilitytab_statusText = await callAPI('load-database-summary');
					}}>DB Summary</button
				>
				<button
					class="btn variant-filled-primary"
					on:click={async () => {
						utilitytab_statusText = await callAPI('reset_portal');
					}}>Reset</button
				>
			</div>
			<div class="flex flex-wrap justify-center space-x-2 mt-4">
				<button
					class="btn variant-filled-secondary"
					on:click={async () => {
						utilitytab_statusText = await callAPI('process-uploads');
					}}>Process Uploads</button
				>
				<button class="btn variant-filled-success">Button 2</button>
				<button class="btn variant-filled-error">Button 3</button>
			</div>
		</div>
		<div class="card variant-glass p-4">
			<h2 class="text-sm font-semibold mb-2">Application Parameters</h2>
			<div class="flex flex-col space-y-1">
				<div class="p-4 mb-4 variant-glass rounded-lg shadow">
					<h3 class="text-sm font-semibold">Portal Paths</h3>
					{#if portalPaths && typeof portalPaths === 'object' && portalPaths.message}
						{#each Object.entries(portalPaths.message) as [key, value]}
							<div class="flex items-center justify-between py-1">
								<span class="text-xs font-semibold">{key}:</span>
								<span class="text-xs ml-2">{value}</span>
							</div>
						{/each}
					{:else}
						<p>Loading data...</p>
					{/if}
				</div>
				<h3 class="text-sm font-semibold">Database Tables Summary</h3>
				<div class="card variant-glass p-4">
					{#if dbstats && typeof dbstats === 'object' && dbstats.message}
						{#each Object.entries(dbstats.message) as [key, value]}
							<div class="flex items-center justify-between py-1">
								<span class="text-xs font-semibold">{key}:</span>
								<span class="text-xs ml-2">{value}</span>
							</div>
						{/each}
					{:else}
						<p>Loading data...</p>
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>
