<script lang="ts">
	import '../app.pcss';
	import '../app.postcss';
	import { AppShell, AppBar } from '@skeletonlabs/skeleton';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { derived } from 'svelte/store';

	// Highlight JS
	import hljs from 'highlight.js/lib/core';
	import 'highlight.js/styles/github-dark.css';
	import { storeHighlightJs } from '@skeletonlabs/skeleton';
	import xml from 'highlight.js/lib/languages/xml'; // for HTML
	import css from 'highlight.js/lib/languages/css';
	import javascript from 'highlight.js/lib/languages/javascript';
	import typescript from 'highlight.js/lib/languages/typescript';

	hljs.registerLanguage('xml', xml); // for HTML
	hljs.registerLanguage('css', css);
	hljs.registerLanguage('javascript', javascript);
	hljs.registerLanguage('typescript', typescript);
	storeHighlightJs.set(hljs);

	// Floating UI for Popups
	import { computePosition, autoUpdate, flip, shift, offset, arrow } from '@floating-ui/dom';
	import { storePopup } from '@skeletonlabs/skeleton';
	storePopup.set({ computePosition, autoUpdate, flip, shift, offset, arrow });
	import { LightSwitch } from '@skeletonlabs/skeleton';

	// Toast to notify incomplete form
	import { initializeStores, Toast } from '@skeletonlabs/skeleton';
	initializeStores();

	import { checkDbConnection } from '$lib/services/apiService';

	let dbStatus = 'Checking...';
	let dbStatusClass = 'badge variant-filled-warning';

	const updateDbStatus = async () => {
		const { status } = await checkDbConnection();
		if (status === 200) {
			dbStatus = 'Connected';
			dbStatusClass = 'badge variant-filled-success';
		} else {
			dbStatus = 'Disconnected';
			dbStatusClass = 'badge variant-filled-error';
		}
	};

	const reactivePage = derived(page, $page => $page);

	reactivePage.subscribe(() => {
		updateDbStatus();
	});

	onMount(() => {
		updateDbStatus();
	});
</script>

<Toast></Toast>
<!-- App Shell -->
<AppShell>
	<svelte:fragment slot="header">
		<!-- App Bar -->
		<AppBar>
			<svelte:fragment slot="lead">
				<div class="flex flex-col items-center">
					<strong class="text-1xl">SignalFlowEEG</strong>
					<span class="text-sm">Analysis Portal</span>
				</div>
			</svelte:fragment>
			<svelte:fragment slot="trail">
				<span class={dbStatusClass}>{dbStatus}</span>
				<LightSwitch></LightSwitch>
				<a
					class="btn btn-sm variant-ghost-surface"
					href="https://discord.gg/EXqV7W8MtY"
					target="_blank"
					rel="noreferrer"
				>
					Discord
				</a>
				<a
					class="btn btn-sm variant-ghost-surface"
					href="https://twitter.com/SkeletonUI"
					target="_blank"
					rel="noreferrer"
				>
					Twitter
				</a>
				<a
					class="btn btn-sm variant-ghost-surface"
					href="https://github.com/skeletonlabs/skeleton"
					target="_blank"
					rel="noreferrer"
				>
					GitHub
				</a>
			</svelte:fragment>
		</AppBar>
	</svelte:fragment>
	<!-- Page Route Content -->
	<slot></slot>
</AppShell>
