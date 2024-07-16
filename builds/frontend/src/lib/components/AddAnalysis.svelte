<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Button } from "$lib/components/ui/button";
  import { addAnalysis, getFormats, getParadigms } from '$lib/services/apiService';

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

  }

  onMount(() => {
    getParadigms()
        .then(result => {
            uniqueParadigms = result.map(item => item.name);
        })
        .catch(error => {
            console.error('Error fetching participants:', error);
            // Handle the error appropriately
        });

    getFormats()
        .then(result => {
            UniqueFormats = result.map(item => item.name);
        })
        .catch(error => {
            console.error('Error fetching participants:', error);
            // Handle the error appropriately
        });
  })

  function handleFormatSelection(event) {
    const selectedFormat = event.target.value;
    newAnalysis.valid_formats.push(selectedFormat);
  }

  function handleParadigmSelection(event) {
    const selectedParadigm = event.target.value;
    newAnalysis.valid_paradigms.push(selectedParadigm);
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
                <option value={formats}>{formats}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="valid_paradigms" class="block text-sm font-semibold text-gray-700 mb-1">Valid Paradigms:</label>
            <select id="valid_paradigms" on:change={handleParadigmSelection} required class="w-full p-2 border rounded" multiple>
              {#each uniqueParadigms as paradigms}
                <option value={paradigms}>{paradigms}</option>
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
        <div class="flex justify-end gap-2">
          <Button type="submit">Add Analysis</Button>
          <Button on:click={closeModal}>Cancel</Button>
        </div>
      </form>
    </dialog>
  </section>
{/if}