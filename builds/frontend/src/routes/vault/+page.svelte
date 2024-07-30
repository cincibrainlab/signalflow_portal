<script lang="ts">
    import EEGStudyVisualizer from '$lib/components/EEGStudyVisualizer.svelte';
    
    /** @type {import('./$types').PageData} */
    export let data;
  </script>
  
  <EEGStudyVisualizer {data} />