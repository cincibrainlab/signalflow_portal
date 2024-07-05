<script lang="ts">
	import '../app.pcss';
	import "../app.css"
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
	let dbStatusClass = 'badge variant-filled-warning h-full md:mx-2 px-1 hidden sm:flex font-bold text-lg';

	const updateDbStatus = async () => {
		const { status } = await checkDbConnection();
		if (status === 200) {
			dbStatus = 'Connected';
			dbStatusClass = 'badge variant-filled-success h-full md:mx-2 px-1 hidden sm:flex font-bold text-lg';
		} else {
			dbStatus = 'Disconnected';
			dbStatusClass = 'badge variant-filled-error h-full md:mx-2 px-1 hidden sm:flex font-bold text-lg';
		}
	};

	onMount(() => {
		updateDbStatus();
	});
</script>

<svelte:head>
  <style>
    body {
      overflow-y: scroll;
    }
  </style>
</svelte:head>

<div class="flex flex-col min-h-screen">
  <div class="navbar container mx-auto">
    <div class="flex-1">
      <a class="btn btn-ghost normal-case text-xl flex items-center" href="/">
        <svg
          width="24"
          height="24"
          viewBox="0 0 120 120"
          xmlns="http://www.w3.org/2000/svg"
          class="mr-2"
        >
          <rect
            x="5"
            y="5"
            width="110"
            height="110"
            rx="10"
            ry="10"
            fill="black"
          />
          <circle
            cx="60"
            cy="50"
            r="30"
            fill="none"
            stroke="white"
            stroke-width="4"
          />
          <path d="M42 50 L60 32 L78 50 L60 68 Z" fill="white" />
          <rect x="30" y="90" width="60" height="10" rx="5" ry="5" fill="white" />
        </svg>
        SignalFlow
      </a>
    </div>
    <div class="flex-none">
      <ul class="menu menu-horizontal px-1 hidden sm:flex font-bold text-lg">
        <li class={dbStatusClass}>{dbStatus}</li>
        <li class="md:mx-4">
          <a
            href="https://github.com/cincibrainlab/sfvault"
            class="border border-primary"
          >
            ★ us on Github
          </a>
        </li>
        <li class="md:mx-2"><a href="/vault">Vault</a></li>
        <li class="md:mx-2"><a href="/upload">Upload</a></li>
        <li class="md:mx-2"><a href="/runmanager">RunManager</a></li>
        <li class="md:mx-2"><a href="/docs">Docs</a></li>
        <li class="md:mx-2"><a rel="external" href="https://cincibrainlab.github.io/signalflow_portal/">Docs</a></li>
        <li class="md:mx-2"><a href="/contact">Contact</a></li>
        <li class="md:mx-2"><a href="/account">Account</a></li>
      </ul>
      <div class="dropdown dropdown-end sm:hidden">
        <!-- svelte-ignore a11y-label-has-associated-control -->
        <!-- svelte-ignore a11y-no-noninteractive-tabindex -->
        <label tabindex="0" class="btn btn-ghost btn-circle">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h7"
            />
          </svg>
        </label>
        <!-- svelte-ignore a11y-no-noninteractive-tabindex -->
        <ul
          tabindex="0"
          class="menu menu-lg dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52 font-bold"
        >
          <li><a href="/blog">Blog</a></li>
          <li><a href="/pricing">Pricing</a></li>
          <li><a href="/account">Account</a></li>
          <li>
            <a
              href="https://github.com/CriticalMoments/CMSaasStarter"
              class="border border-primary"
            >
              ★ us on Github
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>

  <div class="flex-grow">
    <slot />
  </div>

  <div class="bg-gray-50">
    <div class="border-t max-w-[1000px] mx-auto"></div>
    <footer
      class="footer p-10 max-w-7xl mx-auto flex flex-wrap justify-between items-center text-base"
    >
      <nav class="flex flex-wrap justify-center">
        <span class="footer-title opacity-80 w-full text-center mb-2"
          >Explore</span
        >
        <a class="link link-hover mx-2 my-1" href="/vault">Vault</a>
        <a class="link link-hover mx-2 my-1" href="/utilities">Utilities</a>
        <a class="link link-hover mx-2 my-1" href="/features">Features</a>
        <a class="link link-hover mx-2 my-1" href="/docs">Docs</a>
        <a class="link link-hover mx-2 my-1" href="/contact_us">Contact Us</a>
        <a
          class="link link-hover mx-2 my-1"
          href="https://github.com/cincibrainlab/sfvault"
        >
          Github
        </a>
      </nav>
      <aside class="flex flex-col items-center mt-4 sm:mt-0">
        <a
          class="flex flex-col items-center text-center hover:opacity-80 transition-opacity duration-300"
          href="https://github.com/cincibrainlab"
        >
          <img
            alt="Cincinnati Brain Lab Logo"
            src="https://avatars.githubusercontent.com/u/87449739?s=200&v=4"
            class="w-16 h-16 mb-3"
          />
          <div>
            <p class="font-semibold">Cincinnati Brain Lab</p>
            <p class="text-sm text-gray-600">
              Pedapati Neurocomputational Laboratory
            </p>
          </div>
        </a>
        <a
          href="https://github.com/cincibrainlab"
          class="flex items-center justify-center mt-4 hover:opacity-80 transition-opacity duration-300 w-full"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="currentColor"
            class="mr-2"
          >
            <path
              d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
            />
          </svg>
          github.com/cincibrainlab
        </a>
      </aside>
    </footer>
  </div>
</div>

<div class="max-w-5xl mx-auto px-4">
  <!-- Content wrapper -->
</div>
