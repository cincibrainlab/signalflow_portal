<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Button } from "$lib/components/ui/button";
  import { addAnalysis, getFormats, getParadigms, getMatchingFiles } from '$lib/services/apiService';
  import {ChevronDownCircle, FileLineChart} from 'lucide-svelte';
  import { Toast } from 'flowbite-svelte';

  import MultiSelect from 'svelte-multiselect'

  const ui_libs = [`Svelte`, `React`, `Vue`, `Angular`, `...`]

  let selected = []

  export let showModal = false;
  
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
  let uniqueFunctions= ["fakeAnalysis", "test", "test2", "test3"];
  let UniqueCategopries = ["Connectivity", "test", "test2"];
  let UniqueFormats: any[] = [];
  let uniqueParadigms: any[] = [];
  let UniqueFiles: any[] = [];

  async function handleSubmit() {
    try {
      console.log("Trying to add: ", newAnalysis)
      await addAnalysis(newAnalysis);
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
  }


  function findValidFiles(){
    console.log(newAnalysis)
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
            uniqueParadigms = result.map(item => ({ id: item._id, name: item.name }));
        })
        .catch(error => {
            console.error('Error fetching participants:', error);
            // Handle the error appropriately
        });

    getFormats()
        .then(result => {
            UniqueFormats = result.map(item => ({ id: item._id, name: item.name }));
        })
        .catch(error => {
            console.error('Error fetching participants:', error);
            // Handle the error appropriately
        });
  })

  function handleFormatSelection(event) {
    const selectedFormatName = event.target.value;
    const selectedFormat = UniqueFormats.find(format => format.name === selectedFormatName);
    console.log("Selected Format, ", selectedFormat)
    if (selectedFormat) {
      newAnalysis.valid_formats.push(selectedFormat.id);
    }
  }

  function handleParadigmSelection(event) {
    const selectedParadigmName = event.target.value;
    const selectedParadigm = uniqueParadigms.find(paradigm => paradigm.name === selectedParadigmName);
    console.log("Selected Paradigm ", selectedParadigm)
    if (selectedParadigm) {
      newAnalysis.valid_paradigms.push(selectedParadigm.id);
    }
  }

  function dismissAlert() {
      // Perform any actions needed to dismiss the alert for the given file
      console.log(`Alert dismissed`);
      // You can remove the file from the list of validFiles or update its status, etc.
  }
</script>

{#if showModal}
  <section class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
    <dialog class="bg-white rounded-lg p-6 max-w-2xl w-full overflow-auto h-5/6" open>
      <h2 class="text-2xl font-bold mb-4">Add New Analysis</h2>
      <form on:submit|preventDefault={handleSubmit}>
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label for="name" class="block text-sm font-semibold text-gray-700 mb-1">Name:</label>
            <input type="text" id="name" bind:value={newAnalysis.name} required class="w-full p-2 border rounded">
          </div>
          <div>
            <label for="function_name" class="block text-sm font-semibold text-gray-700 mb-1">Function Name:</label>
            <select id="function_name" bind:value={newAnalysis.function_name} required class="w-full p-2 border rounded">
              {#each uniqueFunctions as functions}
                <option value={functions}>{functions}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="valid_formats" class="block text-sm font-semibold text-gray-700 mb-1">Valid Formats:</label>
            <select id="valid_formats" on:change={handleFormatSelection} required class="w-full p-2 border rounded" multiple>
              {#each UniqueFormats as formats}
                <option value={formats.name}>{formats.name}</option>
              {/each}
            </select>
          </div>

          <MultiSelect bind:selected options={ui_libs} />
          <div>
            <label for="valid_paradigms" class="block text-sm font-semibold text-gray-700 mb-1">Valid Paradigms:</label>
            <select id="valid_paradigms" on:change={handleParadigmSelection} required class="w-full p-2 border rounded" multiple>
              {#each uniqueParadigms as paradigms}
                <option value={paradigms.name}>{paradigms.name}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="category" class="block text-sm font-semibold text-gray-700 mb-1">Category:</label>
            <select id="category" bind:value={newAnalysis.category} required class="w-full p-2 border rounded">
              {#each UniqueCategopries as category}
                <option value={category}>{category}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="parameters" class="block text-sm font-semibold text-gray-700 mb-1">Parameters:</label>
            <input type="text" id="parameters" bind:value={newAnalysis.parameters} class="w-full p-2 border rounded">
          </div>
          <div>
            <label for="description" class="block text-sm font-semibold text-gray-700 mb-1">Description:</label>
            <textarea id="description" bind:value={newAnalysis.description} class="w-full p-2 border rounded"></textarea>
          </div>
        </div>

        <div class="flex gap-2">
          <p>Valid Files: </p>
          <Button on:click={findValidFiles}>Check for Valid Files</Button>
        </div>
        <div id="NotificationBox" class="grid grid-cols-2 gap-4 bg-slate-400 p-3 rounded-xl">
          {#each newAnalysis.valid_files as file}
            <Toast class="alert bg-slate-200" style="padding: 10px; margin-bottom: 10px; display: flex; justify-content: space-between;">
              <div>
                  <FileLineChart size=40 strokeWidth=1.5/>
                  <span>{file.original_name}</span>
              </div>
            </Toast>
          {/each}
        </div>

        <div class="flex justify-end gap-2">
          <Button type="submit">Add Analysis</Button>
          <Button on:click={closeModal}>Cancel</Button>
        </div>
      </form>
    </dialog>
  </section>
{/if}