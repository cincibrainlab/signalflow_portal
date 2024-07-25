<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Button } from "$lib/components/ui/button";
  import { addAnalysis, getFormats, getParadigms, getMatchingFiles, getAnalysisFunctions} from '$lib/services/apiService';
  import { createAnalysis } from '$lib/services/prefectAPI';
  import { Checkbox } from 'flowbite-svelte';

  import MultiSelect from 'svelte-multiselect'


  let selectedFormats = []
  let selectedParadigms = []

  export let showModal = false;
  let runAnalysis_choice = false;
  let added_analysis_id: string
  
  const dispatch = createEventDispatcher();

  let newAnalysis = {
    name: '',
    analysis_function: '',
    description: '',
    category: '',
    valid_formats: [],
    valid_paradigms: [],
    valid_files: [],
    parameters: ''
  };

  // These should be fetched from your API or passed as props
  let uniqueFunctions: any[] = [];
  let UniqueCategopries = ["Connectivity", "test", "test2"];
  let UniqueFormats: any[] = [];
  let uniqueParadigms: any[] = [];
  let UniqueFiles: any[] = [];

  async function handleSubmit() {
    try {
      await getMatchingFiles(newAnalysis.valid_formats, newAnalysis.valid_paradigms)
      .then(result => {
            console.log(result)
            newAnalysis.valid_files = result.map(file => file._id)
        })
        .catch(error => {
            console.error('Error fetching files:', error);
            // Handle the error appropriately
        });
      console.log("Trying to add: ", newAnalysis)
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
      analysis_function: '',
      description: '',
      category: '',
      valid_formats: [],
      valid_paradigms: [],
      valid_files: [],
      parameters: ''
    };
    selectedFormats = []
    selectedParadigms = []
    runAnalysis_choice = false;
    added_analysis_id = ""
  }



  onMount(() => {
    getParadigms()
        .then(result => {
            console.log(result)
            uniqueParadigms = result.map(item => ({ id: item._id, label: item.name }));
        })
        .catch(error => {
            console.error('Error fetching paradigms:', error);
            // Handle the error appropriately
        });

    getFormats()
        .then(result => {
            UniqueFormats = result.map(item => ({ id: item._id, label: item.name }));
        })
        .catch(error => {
            console.error('Error fetching formats:', error);
            // Handle the error appropriately
        });

    getAnalysisFunctions()
        .then(result => {
          console.log(result)
          uniqueFunctions = result
        })
        .catch(error => {
            console.error('Error fetching functions:', error);
            // Handle the error appropriately
        });
  })

  function handleFormatSelection(event){
    newAnalysis.valid_formats = selectedFormats.map(format => format.id )
  }


  function handleParadigmSelection(event) {
    newAnalysis.valid_paradigms = selectedParadigms.map(paradigm => paradigm.id)
  }



</script>

{#if showModal}
  <section class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
    <dialog class="bg-white rounded-lg p-6 max-w-2xl w-full overflow-auto h-5/6" open>
      <h2 class="text-2xl font-bold mb-4">Add New Analysis</h2>
      <form on:submit|preventDefault={handleSubmit}>
        <div class="mb-4">
          <div>
            <label for="name" class="block text-md font-semibold text-gray-700 mb-1">Name:</label>
            <input type="text" id="name" bind:value={newAnalysis.name} required class="w-full p-2 border rounded">
          </div>
          <div>
            <label for="analysis_function" class="block text-md font-semibold text-gray-700 mb-1">Function Name:</label>
            <select id="analysis_function" bind:value={newAnalysis.analysis_function} required class="w-full p-2 border rounded">
              {#each uniqueFunctions as analysisFunction}
                <option value={analysisFunction._id}>{analysisFunction.name}</option>
              {/each}
            </select>
          </div>

          <div>
            <label for="valid_formats" class="block text-md font-semibold text-gray-700 mb-1">Valid Formats:</label>
            <MultiSelect 
                bind:selected = {selectedFormats} 
                options={UniqueFormats} 
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
              {#each UniqueCategopries as category}
                <option value={category}>{category}</option>
              {/each}
            </select>
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