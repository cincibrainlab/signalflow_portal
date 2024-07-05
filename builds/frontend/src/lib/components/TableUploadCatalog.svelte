<script lang="ts">
	import { onMount } from 'svelte';
	import type { DataHandler } from '@vincjo/datatables';
	import ThSort from '$lib/components/client/ThSort.svelte';
	import ThFilter from '$lib/components/client/ThFilter.svelte';
	import Search from '$lib/components/client/Search.svelte';
	import RowsPerPage from '$lib/components/client/RowsPerPage.svelte';
	import RowCount from '$lib/components/client/RowCount.svelte';
	import Pagination from '$lib/components/client/Pagination.svelte';

	import type { UploadRow } from '$lib/types';

	import { popup } from '@skeletonlabs/skeleton';
	import type { PopupSettings } from '@skeletonlabs/skeleton';

	export let handler: DataHandler<UploadRow>;

	let rows: UploadRow[] = [];
	

	$: {
		handler.getRows().subscribe((value) => {
			rows = value;
			console.log('Rows updated:', JSON.stringify(rows, null, 2));
		});
	}

	onMount(() => {
		console.log('TableUploadCatalog mounted');
		console.log('Initial rows:', JSON.stringify(rows, null, 2));
	});

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
			<ThSort {handler} orderBy="size">Size (MB)</ThSort>
			<ThSort {handler} orderBy="date_added">Date Added</ThSort>
		</tr>
	</thead>
	<tbody>
		{#if rows.length === 0}
			<tr>
				<td colspan="6">No data available</td>
			</tr>
		{:else}
			{#each rows as row (row.upload_id)}
				<tr on:click={() => console.log(row)}>
					<td>
						{#if row.original_name}
							<span
								class="badge oval bg-initial [&>*]:pointer-events-none"
								use:popup={{
									event: 'hover',
									target: `popupHover-${row.upload_id}`,
									placement: 'top'
								}}
							>
								{row.original_name}
							</span>
							<div
								class="card p-4 variant-filled-primary"
								data-popup={`popupHover-${row.upload_id}`}
							>
								<div class="info-card">
									<h4 class="info-card-title">Upload Info:</h4>
									<ul class="info-list">
										<li>
											<strong>File Name:</strong> {row.original_name}
										</li>
										<li>
											<strong>Date Added:</strong>
											{new Date(row.date_added).toLocaleDateString('en-US', {
												year: '2-digit',
												month: 'numeric',
												day: 'numeric'
											})}
										</li>
										<li>
											<strong>Email:</strong> {row.upload_email}
										</li>
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
						{#if row.size}
							<span class="badge bg-initial">{(row.size / 1024 / 1024).toFixed(2)}</span>
						{:else}
							<span class="badge bg-initial">missing</span>
						{/if}
					</td>
					<td>
						{#if row.date_added}
							<span class="badge bg-initial"
								>{new Date(row.date_added).toLocaleDateString('en-US', {
									year: '2-digit',
									month: 'numeric',
									day: 'numeric'
								})}</span
							>
						{:else}
							<span class="badge bg-initial">missing</span>
						{/if}
					</td>
					<input type="hidden" name="hash" value={row.hash} />
					<input type="hidden" name="upload_id" value={row.upload_id} />
				</tr>
			{/each}
		{/if}
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
		background: var(--skeleton-ui-color, #f3f4f6); /* Default fallback color is a light grey */
		transition: background 0.2s;
	}
	td {
		padding: 4px 20px;
		border-bottom: 1px solid #eee;
	}
</style>

