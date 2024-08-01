<script lang="ts">
    import { Button } from "$lib/components/ui/button";
    import { goto } from '$app/navigation';
    import { Input } from "$lib/components/ui/input"
    import { debounce } from 'lodash-es';
    import { getAnalyses } from '$lib/services/apiService';
    import { Alert} from 'flowbite-svelte';

    import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "$lib/components/ui/table"
  import {
    ArrowUpDown,
	  Filter,
  } from "lucide-svelte"
	import AddAnalysis from '$lib/components/AddAnalysis.svelte';
	import { fade } from "svelte/transition";
  /** @type {import('./$types').PageData} */
  export let data;

  let { analyses, uniqueParadigms, uniqueFormats, uniqueFlows, uniqueCategories } = data;
  uniqueParadigms = uniqueParadigms.filter((item: any) => item.name !== "Unassigned");
  uniqueFormats = uniqueFormats.filter((item: any) => item.name !== "Unassigned");

  function openDashboard(id: string) {
      goto(`/dashboard?id=${id}`);
  }

  let showAddAnalysisModal = false;

  let sortColumn: string = ""
  let sortDirection: "asc" | "desc" = "asc"

  let searchTerm = '';
  let debouncedSearchTerm = "";
  let selectedFunction: string = "All"
  let selectedParadigm: string = "All"
  let selectedFormat: string = "All"

  let filteredanalyses: any = []
  let isFiltering = false;

  const updateDebouncedSearch = debounce((value: any) => {
    debouncedSearchTerm = value;
  }, 300);

  $: {
    updateDebouncedSearch(searchTerm);
  }

  $: {
    isFiltering = true;
    filteredanalyses = analyses.filter((analysis: any) => {

      const matchesSearch =
        analysis.name.toLowerCase().includes(debouncedSearchTerm.toLowerCase()) ||
        analysis?.category.toLowerCase().includes(debouncedSearchTerm.toLowerCase());

      const matchesFunction =
        selectedFunction === "All" ||
        analysis?.analysis_function === selectedFunction;

      const matchesFormat =
        selectedFormat === "All" ||
        analysis?.valid_formats.includes(selectedFormat);

      const matchesParadigm =
        selectedParadigm === "All" ||
        analysis?.valid_paradigms.includes(selectedParadigm);

      return matchesSearch && matchesFunction  && matchesFormat && matchesParadigm;
    }).sort((a: any, b: any) => {
      if (!sortColumn) return 0;
      
      let aValue, bValue;
      switch (sortColumn) {
        case "name":
          aValue = a.name;
          bValue = b.name;
          break;

        case "flow":
          aValue = a.analysis_flow;
          bValue = b.analysis_flow;
          break;

        case "category":
          aValue = a.category;
          bValue = b.category;
          break;

        case "formats":
          aValue = a.valid_formats.join(",");
          bValue = b.valid_formats.join(",");
          break;

        case "paradigms":
          aValue = a.eeg_paradigm.map((p: any) => p.type).join(",");
          bValue = b.eeg_paradigm.map((p: any) => p.type).join(",");
          break;
      }
      
      // Handle undefined or null values
      if (aValue === undefined || aValue === null) return 1;
      if (bValue === undefined || bValue === null) return -1;
      
      // Compare values
      if (aValue < bValue) return sortDirection === "asc" ? -1 : 1;
      if (aValue > bValue) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });
    isFiltering = false;
  }

  function toggleSort(column: string) {
    console.log("Toggling sort for column:", column)
    if (sortColumn === column) {
      sortDirection = sortDirection === "asc" ? "desc" : "asc"
    } else {
      sortColumn = column
      sortDirection = "asc"
    }
    console.log("New sort column:", sortColumn)
    console.log("New sort direction:", sortDirection)
  }

  let toastMessage = '';
  let toastType: 'success' | 'error' = 'success';
  let showToast = false;

  function handleToast(event: CustomEvent) {
    ({ message: toastMessage, type: toastType } = event.detail);
    showToast = true;
    setTimeout(() => showToast = false, 3000);
  }

  async function handleAnalysisAdded() {
    analyses = await getAnalyses();
    showAddAnalysisModal = false;
  }
    
</script>

<div class="mx-auto p-4">
    <div class="mb-6 p-4 rounded-lg shadow">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold flex items-center">
            <Filter class="w-5 h-5 mr-2" />
            Filters
          </h2>

          <AddAnalysis 
            bind:showModal={showAddAnalysisModal} 
            on:close={async () => {
              showAddAnalysisModal = false;
              analyses = await getAnalyses();
            }}
            on:showToast={handleToast}
            {uniqueParadigms}
            {uniqueFormats}
            {uniqueFlows}
            {uniqueCategories}
          />
          <Button  on:click={() => showAddAnalysisModal = true}>
            Add New Analysis
          </Button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label for="search" class="block text-sm font-medium mb-1"
              >Search</label
            >
            <Input
              class= "h-9"
              type="text"
              id="search"
              placeholder="Search by name or category"
              bind:value={searchTerm}
            />
          </div>
          <div>
            <label
              for="Flow"
              class="block text-sm font-medium0 mb-1">Flow</label
            >
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 " bind:value={selectedFunction}>
              <option value="All">All</option>
              {#each uniqueFlows as flow}
                <option value={flow.name}>{flow.name}</option>
              {/each}
            </select>
          </div>
          <div>
            <label
              for="Format"
              class="block text-sm font-medium0 mb-1">Format</label
            >
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 " bind:value={selectedFormat}>
              <option value="All">All</option>
              {#each uniqueFormats as format}
                <option value={format.name}>{format.name}</option>
              {/each}
            </select>
          </div>
          <div>
            <label 
              for="Paradigm"
              class="block text-sm font-medium0 mb-1">Paradigm</label
            >
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 " bind:value={selectedParadigm}>
              <option value="All">All</option>
              {#each uniqueParadigms as paradigm}
                <option value={paradigm.name}>{paradigm.name}</option>
              {/each}
            </select>
          </div>
        </div>
    </div>
  
    <Table>
        <TableHeader>
            <TableRow>
                <TableHead class="w-1/8" on:click={() => toggleSort("name")}>
                    Analysis Name
                    <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
                </TableHead>
                <TableHead class="w-1/8" on:click={() => toggleSort("flow")}>
                    Flow
                    <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
                </TableHead>
                <TableHead class="w-1/8" on:click={() => toggleSort("category")}>
                    Category
                    <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
                </TableHead>
                <TableHead class="w-1/8" on:click={() => toggleSort("formats")}>
                    Formats
                    <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
                </TableHead>
                <TableHead class="w-1/8" on:click={() => toggleSort("paradigms")}>
                    Paradigms
                    <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
                </TableHead>
            </TableRow>
        </TableHeader>
        <TableBody>
            {#each filteredanalyses as analysis}
                <TableRow>
                    <TableCell>{analysis.name}</TableCell>
                    <TableCell>{analysis.analysis_flow}</TableCell>
                    <TableCell>{analysis.category}</TableCell>
                    <TableCell>{analysis.valid_formats.join(', ')}</TableCell>
                    <TableCell>{analysis.valid_paradigms.join(', ')}</TableCell>
                    <TableCell>
                        <Button on:click={() => openDashboard(analysis.deployment_id)}>Open Dashboard</Button>
                    </TableCell>
                </TableRow>
            {/each}
        </TableBody>
    </Table>
</div>
{#if showToast}
  <div 
    class="toast toast-top toast-end"
    transition:fade
  >
    <Alert class="{toastType === 'success' ? 'bg-green-300' : 'bg-red-300'} shadow-lg hover:shadow-xl">
      <span class="text-base">{toastMessage}</span>
    </Alert>
  </div>
{/if}