<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Button } from "$lib/components/ui/button";
  import { addAnalysis, getFormats, getParadigms, getMatchingFiles, getAnalysisFunctions, runAnalysis} from '$lib/services/apiService';
  import { Checkbox } from 'flowbite-svelte';

  import MultiSelect from 'svelte-multiselect'


  let selectedFormats = []
  let selectedParadigms = []
  let test: any

  export let showModal = false;
  let runAnalysis_choice = false;
  let added_analysis_id: string
  
  const dispatch = createEventDispatcher();

  let newAnalysis = {
    name: '',
    function_name: '',
    description: '',
    category: '',
    valid_formats: [],
    valid_paradigms: [],
    valid_files: [],
    files: [],
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
      newAnalysis.valid_files = newAnalysis.valid_files.map(file => file._id)
      newAnalysis.files = newAnalysis.files.map(file => file._id)
      console.log("Trying to add: ", newAnalysis)
      await addAnalysis(newAnalysis)
      .then(result => {
        console.log(result)
        added_analysis_id = result.analysisId
        if (runAnalysis_choice){
          runAnalysis(added_analysis_id)
        }
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
      function_name: '',
      description: '',
      category: '',
      valid_formats: [],
      valid_paradigms: [],
      valid_files: [],
      files: [],
      parameters: ''
    };
    selectedFormats = []
    selectedParadigms = []
    runAnalysis_choice = false;
    added_analysis_id = ""
  }


  function findValidFiles(){
      getMatchingFiles(newAnalysis.valid_formats, newAnalysis.valid_paradigms)
      .then(result => {
            newAnalysis.valid_files = result
        })
        .catch(error => {
            console.error('Error fetching participants:', error);
            // Handle the error appropriately
        });
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

  function toggleFileSelection(checked:boolean, file){
    if (checked) {
        newAnalysis.files = [...newAnalysis.files, file];
    } else {
        newAnalysis.files = newAnalysis.files.filter(f => f._id !== file._id);
    }
  }

</script>

{#if showModal}
  <section class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
    <dialog class="bg-white rounded-lg p-6 max-w-2xl w-full overflow-auto h-5/6" open>
      <h2 class="text-2xl font-bold mb-4">Add New Analysis</h2>
      <form on:submit|preventDefault={handleSubmit}>
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label for="name" class="block text-md font-semibold text-gray-700 mb-1">Name:</label>
            <input type="text" id="name" bind:value={newAnalysis.name} required class="w-full p-2 border rounded">
          </div>
          <div>
            <label for="function_name" class="block text-md font-semibold text-gray-700 mb-1">Function Name:</label>
            <select id="function_name" bind:value={newAnalysis.function_name} required class="w-full p-2 border rounded">
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
            <label for="parameters" class="block text-md font-semibold text-gray-700 mb-1">Parameters:</label>
            <input type="text" id="parameters" bind:value={newAnalysis.parameters} class="w-full p-2 border rounded">
          </div>
          <div>
            <label for="description" class="block text-md font-semibold text-gray-700 mb-1">Description:</label>
            <textarea id="description" bind:value={newAnalysis.description} class="w-full p-2 border rounded"></textarea>
          </div>
        </div>

        <div class = "flex justify-between">
          <div>
            <label for="valid_files" class="block text-md font-semibold text-gray-700">Valid Files:</label>
            <p class="text-sm font-medium text-gray-500 mb-1">Select the desired files for the analysis to run on</p>            
          </div>
          <Button on:click={findValidFiles}>Check for Valid Files</Button>
        </div>
        <div id="NotificationBox" class="gap-4 bg-gray-300 p-3 rounded-xl h-40">
          <div class = "rounded-lg bg-white">
            {#each newAnalysis.valid_files as file}
              <div class="border-b-2 border-gray-200 dark:border-gray-700">
                <Checkbox on:change={(event) => toggleFileSelection(event.target.checked, file)} class="w-full rounder-xl p-2">
                  <span class="pl-2">{file.original_name}</span>
                </Checkbox>
              </div>
            {/each}
          </div>
        </div>
        <p>{newAnalysis.files}</p>

        <div class="absolute bottom-6 left-6 right-6 flex justify-between gap-2 mt-2">
          <Button class="p-5" variant="outline" on:click={closeModal}>Cancel</Button>
          <div>
            <Button class="p-5" type="submit">Save Analysis</Button>
            <Button class="p-5" on:click={() => runAnalysis_choice = true} type="submit">Save and Run</Button>
          </div>
          
        </div>
      </form>
    </dialog>
  </section>
{/if}