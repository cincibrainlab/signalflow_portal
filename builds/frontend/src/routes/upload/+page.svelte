<script lang="ts">
	import { onMount } from 'svelte';
	import type { SvelteComponent } from 'svelte';

	import { TabGroup, Tab } from '@skeletonlabs/skeleton';
	import { writable } from 'svelte/store';

	// Custom UI Components
	import UploadForm from '$lib/components/UploadFormTab.svelte';
	import Datatable from '$lib/components/FileTableTab.svelte';
	import Utilities from '$lib/components/UtilitiesTab.svelte';
	import fetchCatalogData from '$lib/components/FileTableTab.svelte';

	onMount(async () => {});

	const activeTab = writable('upload');

	$: if ($activeTab === 'files') {
		//console.log('Fetching catalog data...');
	}
</script>

<div class="max-w-4xl mx-auto px-4 py-6">
	<TabGroup justify="justify-center">
		{#each [{ name: 'upload', label: 'Upload Portal' }, { name: 'jobs', label: 'Job List' }, { name: 'files', label: 'File List' }, { name: 'utilities', label: 'Utilities' }] as tab}
			<Tab bind:group={$activeTab} name={tab.name} value={tab.name}>
				<span>{tab.label}</span>
			</Tab>
		{/each}

		<!-- Tab Panels -->
		<svelte:fragment slot="panel">
			{#each [{ tabName: 'upload', component: UploadForm }, { tabName: 'jobs', component: null }, { tabName: 'files', component: Datatable }, { tabName: 'utilities', component: Utilities }] as { tabName, component }}
				<div class="tab-content" class:active={$activeTab === tabName}>
					{#if $activeTab === 'files' && component}
						<svelte:component this={component}  />
					{:else if component}
						<svelte:component this={component} />
					{/if}
				</div>
			{/each}
		</svelte:fragment>
	</TabGroup>
</div>

<style>
	.tab-content {
		display: none;
	}

	.active {
		display: block;
	}
</style>