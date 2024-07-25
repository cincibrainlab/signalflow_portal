<script lang="ts">
    import { onMount } from 'svelte';
    import { Button } from "$lib/components/ui/button";
    import { getAnalyses } from '$lib/services/apiService';
    import { goto } from '$app/navigation';
    import { Input } from "$lib/components/ui/input"

    import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "$lib/components/ui/table"
  import {
    ExternalLink,
    ArrowUpDown,
	Filter,
  } from "lucide-svelte"
	import AddAnalysis from '$lib/components/AddAnalysis.svelte';

    let analyses: any[] = [];

    onMount(async () => {
        try {
            analyses = await getAnalyses();
            console.log(analyses);
        } catch (error) {
            console.error('Error fetching analyses (page):', error);
        }
    });

    function viewDetails(id: string) {
        console.log(`View details for analysis ${id}`);
        // Implement view details functionality
    }

    function openDashboard(id: string) {
        goto(`/dashboard?id=${id}`);
    }

    let showAddAnalysisModal = false;
    let searchTerm = '';
    let selectedFunction = '';
    let selectedCategory = '';
    let selectedParadigm = '';
    
</script>

<div class="mx-auto p-4">
    <div class="mb-6 bg-white p-4 rounded-lg shadow">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold flex items-center">
            <Filter class="w-5 h-5 mr-2" />
            Filters
          </h2>

  
          <AddAnalysis 
            bind:showModal={showAddAnalysisModal} 
            on:close={() => showAddAnalysisModal = false}
          />
          <Button variant="outline" on:click={() => showAddAnalysisModal = true}>
            Add New Analysis
          </Button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label for="search" class="block text-sm font-medium text-gray-700 mb-1"
              >Search</label
            >
            <Input
              class= "h-9"
              type="text"
              id="search"
              placeholder="Search by EEGID or Participant ID"
              bind:value={searchTerm}
            />
          </div>
          <div>
            <label
              for="Function"
              class="block text-sm font-medium text-gray-7000 mb-1">Function</label
            >
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 " bind:value={selectedFunction}>
              <!-- {#each uniqueFunctions as function}
                <option value={function}>{function}</option>
              {/each} -->
            </select>
          </div>
          <div>
            <label
              for="Format"
              class="block text-sm font-medium text-gray-7000 mb-1">Format</label
            >
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 " bind:value={selectedCategory}>
            </select>
          </div>
          <div>
            <label 
              for="Paradigm"
              class="block text-sm font-medium text-gray-7000 mb-1">Paradigm</label
            >
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 " bind:value={selectedCategory}>
            </select>
          </div>
          <!-- <div>
            <label
              for="diagnosis"
              class="block text-sm font-medium text-gray-700 mb-1">Diagnosis</label
            >
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 " bind:value={selectedDiagnosis}>
              {#each uniqueDiagnoses as diagnosis}
                <option value={diagnosis}>{diagnosis}</option>
              {/each}
            </select>
          </div>
          <div>
            <label
              for="ageGroup"
              class="block text-sm font-medium text-gray-700 mb-1">Age Group</label
            >
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 " bind:value={selectedAgeGroup}>
              {#each uniqueAgeGroups as ageGroup}
                <option value={ageGroup}>{ageGroup}</option>
              {/each}
          </div>
          <div>
            <label
              for="paradigm"
              class="block text-sm font-medium text-gray-700 mb-1">Paradigm</label
            >
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 " bind:value={selectedParadigm}>
              {#each uniqueParadigms as paradigm}
                <option value={paradigm}>{paradigm.replace("_", " ")}</option>
              {/each}
            </select>
          </div> -->
        </div>
    </div>
  
    <Table>
        <TableHeader>
            <TableRow>
                <TableHead>
                    Analysis Name
                </TableHead>
                <TableHead>
                    Function
                </TableHead>
                <TableHead>
                    Category
                </TableHead>
                <TableHead>
                    Formats
                </TableHead>
                <TableHead>
                    Paradigms
                </TableHead>
            </TableRow>
        </TableHeader>
        <TableBody>
            {#each analyses as analysis}
                <TableRow>
                    <TableCell>{analysis.name}</TableCell>
                    <TableCell>{analysis.analysis_function}</TableCell>
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