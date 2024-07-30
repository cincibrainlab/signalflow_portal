<script lang="ts">
  import { createEventDispatcher} from 'svelte';
  import { Button } from "$lib/components/ui/button";
  import { addAnalysis, getMatchingFiles } from '$lib/services/apiService';

  import MultiSelect from 'svelte-multiselect'


  let selectedFormats: any[] = []
  let selectedParadigms: any[] = []

  let runAnalysis_choice = false;
  let added_analysis_id: string
  
  const dispatch = createEventDispatcher();

  interface Analysis {
    name: string;
    analysis_flow: string;
    description: string;
    category: string;
    valid_formats: string[]; // or any other specific type
    valid_paradigms: string[]; // or any other specific type
    valid_files: string[]; // or any other specific type
    output_path: string;
    parameters: string;
  }

  let newAnalysis: Analysis = {
    name: '',
    analysis_flow: '',
    description: '',
    category: '',
    valid_formats: [] as string[], // specify the type here
    valid_paradigms: [] as string[], // specify the type here
    valid_files: [] as string[], // specify the type here
    output_path: '',
    parameters: ''
  };

  // These should be fetched from your API or passed as props
    export let showModal = false;
    export let uniqueParadigms: any[] = [];
    export let uniqueFormats: any[] = [];
    export let uniqueFlows: any[] = [];
    export let uniqueCategories: string[] = [];

  async function handleSubmit() {
    try {
      await getMatchingFiles(newAnalysis.valid_formats, newAnalysis.valid_paradigms)
        .then(result => {
            console.log(result)
            newAnalysis.valid_files = result.map((file: any) => file._id)
        })
          .catch(error => {
              console.error('Error fetching files:', error);
              // Handle the error appropriately
          });
      console.log("Trying to add: ", newAnalysis)
      if (newAnalysis.output_path == "") {
        newAnalysis.output_path = "portal_files/output/"
      }
      await addAnalysis(newAnalysis)
      .then(result => {
        console.log(result)
      })
      .catch(error => {console.error('Error adding analysis:', error);});
      dispatch('analysisAdded', newAnalysis);
      closeModal();
    } catch (error) {
      console.error('Error adding new analysis:', error);
      // Handle error (e.g., show an error message to the user)
    }
  }


  function closeModal() {
    showModal = false;
    dispatch('close');
    // Reset the form
    newAnalysis = {
      name: '',
      analysis_flow: '',
      description: '',
      category: '',
      valid_formats: [] as string[], // specify the type here
      valid_paradigms: [] as string[], // specify the type here
      valid_files: [] as string[], // specify the type here
      output_path: '',
      parameters: ''
    };
    selectedFormats = []
    selectedParadigms = []
    runAnalysis_choice = false;
    added_analysis_id = ""
  }


  function handleFormatSelection(event: any){
    newAnalysis.valid_formats = selectedFormats.map(format => format.id )
  }


  function handleParadigmSelection(event: any) {
    newAnalysis.valid_paradigms = selectedParadigms.map(paradigm => paradigm.id)
  }

</script>

{#if showModal}
  <section class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-20" role="dialog" aria-modal="true">
    <dialog class="bg-white rounded-lg p-6 max-w-2xl w-full overflow-auto h-5/6" open>
      <h2 class="text-2xl font-bold mb-4">Add New Analysis</h2>
      <form on:submit|preventDefault={handleSubmit}>
        <div class="mb-4">
          <div>
            <label for="name" class="block text-md font-semibold text-gray-700 mb-1">Name:</label>
            <input type="text" id="name" bind:value={newAnalysis.name} required class="w-full p-2 border rounded">
          </div>
          <div>
            <label for="analysis_flow" class="block text-md font-semibold text-gray-700 mb-1">Function Name:</label>
            <select id="analysis_flow" bind:value={newAnalysis.analysis_flow} required class="w-full p-2 border rounded">
              {#each uniqueFlows as analysisFlow}
                <option value={analysisFlow._id}>{analysisFlow.name}</option>
              {/each}
            </select>
            <p>Selected Flow: {newAnalysis.analysis_flow}</p>
          </div>

          <div>
            <label for="valid_formats" class="block text-md font-semibold text-gray-700 mb-1">Valid Formats:</label>
            <MultiSelect 
                bind:selected = {selectedFormats} 
                options={uniqueFormats} 
                on:change={handleFormatSelection}
                required
            />
            <p>Selected Formats: {JSON.stringify(newAnalysis.valid_formats)}</p>
          </div>

          <div>
            <label for="valid_paradigms" class="block text-md font-semibold text-gray-700 mb-1">Valid Paradigms:</label>
            <MultiSelect 
                bind:selected = {selectedParadigms} 
                options={uniqueParadigms} 
                on:change={handleParadigmSelection}
                required
            />
            <p>Selected Paradigms: {JSON.stringify(newAnalysis.valid_paradigms)}</p>
          </div>
          <div>
            <label for="category" class="block text-md font-semibold text-gray-700 mb-1">Category:</label>
            <select id="category" bind:value={newAnalysis.category} required class="w-full p-2 border rounded">
              {#each uniqueCategories as category}
                <option value={category}>{category}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="output_path" class="block text-md font-semibold text-gray-700 mb-1">Output Path:</label>
            <input 
              type="text" 
              id="output_path" 
              bind:value={newAnalysis.output_path}
              placeholder="Default: portal_files/output"
              class="w-full p-2 border rounded"
            >
          </div>
          <div>
            <label for="description" class="block text-md font-semibold text-gray-700 mb-1">Description:</label>
            <textarea id="description" bind:value={newAnalysis.description} class="w-full p-2 border rounded"></textarea>
          </div>
        </div>
        <div class="absolute bottom-6 left-6 right-6 flex justify-between gap-2 mt-2">
          <Button class="p-5" variant="outline" on:click={closeModal}>Cancel</Button>
          <div>
            <Button class="p-5" type="submit">Create Analysis</Button>
          </div>
          
        </div>
      </form>
    </dialog>
  </section>
{/if}