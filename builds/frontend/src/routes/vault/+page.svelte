<script lang="ts">
    import EEGStudyVisualizer from '$lib/components/EEGStudyVisualizer.svelte';
    
    import type { PageData } from './$types';
    export let data: PageData;
  </script>
  
  <svelte:head>
    <link rel="modulepreload" href="/src/lib/components/EEGStudyVisualizer.svelte" />
  </svelte:head>
  
  <EEGStudyVisualizer {data} />