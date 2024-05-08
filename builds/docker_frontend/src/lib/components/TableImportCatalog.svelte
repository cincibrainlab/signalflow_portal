<script lang="ts">
	import { onMount } from 'svelte';
	import type { DataHandler } from '@vincjo/datatables';
	import ThSort from '$lib/components/client/ThSort.svelte';
	import ThFilter from '$lib/components/client/ThFilter.svelte';
	import Search from '$lib/components/client/Search.svelte';
	import RowsPerPage from '$lib/components/client/RowsPerPage.svelte';
	import RowCount from '$lib/components/client/RowCount.svelte';
	import Pagination from '$lib/components/client/Pagination.svelte';

	import { popup } from '@skeletonlabs/skeleton';
	import type { PopupSettings } from '@skeletonlabs/skeleton';

	import type { ImportRow } from '$lib/types';

	export let handler: DataHandler<ImportRow>;

	onMount(() => {});

	const rows = handler.getRows();

	const popupHover: PopupSettings = {
		event: 'hover',
		target: 'popupHover',
		placement: 'top'
	};

</script>

<header></header>
<table>
	<thead>
		<tr>
			<ThSort {handler} orderBy="original_name">Name</ThSort>
			<ThSort {handler} orderBy="dataset_name">Dataset</ThSort>
			<ThSort {handler} orderBy="eeg_format">Format</ThSort>
			<ThSort {handler} orderBy="eeg_paradigm">Paradigm</ThSort>
			<ThSort {handler} orderBy="has_fdt_file">hasFDT</ThSort>
			<ThSort {handler} orderBy="n_epochs">Epochs</ThSort>
			<ThSort {handler} orderBy="total_samples">Samples</ThSort>
		</tr>
	</thead>
	<tbody>
		{#await $rows}
			<p>Loading...</p>
		{:then rows}
			{#each rows as row (row.upload_id)} <!-- Added key to each block for reactivity -->
				<tr on:click={() => console.log(row.upload_id)}>
					<td>
						{#if row.original_name}
							<span class="badge oval bg-initial [&>*]:pointer-events-none" use:popup={{
								event: 'hover',
								target: `popupHover-${row.upload_id}`,
								placement: 'top'
							  }}>
							  {row.original_name}
							</span>
							<div class="card p-4 variant-filled-primary" data-popup={`popupHover-${row.upload_id}`}>
								<div class="info-card">
									<h4 class="info-card-title">EEG Info:</h4>
									<ul class="info-list">
										<li><strong>Sample Rate:</strong> {row.sample_rate} Hz</li>
										<li><strong>Channels:</strong> {row.n_channels}</li>
										<li><strong>Epochs:</strong> {row.n_epochs}</li>
										<li><strong>Total Samples:</strong> {(row.total_samples / 1000).toFixed(0)}K</li>
										<li><strong>Date Added:</strong> {new Date(row.date_added).toLocaleDateString('en-US', {
											year: '2-digit', 
											month: 'numeric',
											day: 'numeric'
										})}</li>
									</ul>
								</div>
								<div class="arrow variant-filled-secondary" />
							</div>
						{:else}
							<span class="badge badge-ghost-warning">missing</span>
						{/if}
					</td>
					<td>
						{#if row.dataset_name}
							{#if row.dataset_id}
								{@const [datasetId, badgeColor] = row.dataset_id.split('|')}
								<span class="badge oval" style="background-color: {badgeColor};">{row.dataset_name}</span>
							{:else}
								<span class="badge oval variant-soft-primary">{row.dataset_name}</span>
							{/if}
						{:else}
							<span class="badge oval variant-filled-warning">missing</span>
						{/if}
					</td>	
					<td>
						{#if row.eeg_format}
							<span class="badge oval variant-soft-tertiary">{row.eeg_format}</span>
						{:else}
							<span class="badge oval variant-filled-warning">missing</span>
						{/if}
					</td>
					<td>
						{#if row.eeg_paradigm}
							<span class="badge oval variant-soft-secondary">{row.eeg_paradigm}</span>
						{:else}
							<span class="badge oval variant-filled-warning">missing</span>
						{/if}
					</td>
					<td>
						{#if row.has_fdt_file === true}
							<span class="badge variant-filled-success">Yes</span>
						{:else if row.has_fdt_file === false}
							<span class="badge variant-filled-error">No</span>
						{:else}
							<span class="badge variant-filled-warning">Unknown</span>
						{/if}
					</td>
				
					<td>
						{#if row.n_epochs}
							<span class="badge bg-initial">{row.n_epochs}</span>
						{:else}
							<span class="badge bg-initial">missing</span>
						{/if}
					</td>
					<td>
						{#if row.total_samples}
							<span class="badge bg-initial">{(row.total_samples / 1000).toFixed(0)}K</span>
						{:else}
							<span class="badge bg-initial">missing</span>
						{/if}
					</td>
					<input type="hidden" name="hash" value={row.hash} />
					<input type="hidden" name="upload_id" value={row.upload_id} />
				</tr>
			{/each}
		{:catch error}
			<p>Error loading data.</p>
		{/await}
	</tbody>
</table>
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
</style>
