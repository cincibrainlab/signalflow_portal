<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Button } from "$lib/components/ui/button";
  import { addAnalysis, getMatchingFiles, getMatchingTaggedFiles } from '$lib/services/apiService';
  import { Tabs, TabsList, TabsTrigger } from "$lib/components/ui/tabs";
  import * as Tooltip from "$lib/components/ui/tooltip/index.js";



  import MultiSelect from 'svelte-multiselect'
	import Input from './ui/input/input.svelte';
  import * as Select from '$lib/components/ui/select';


  let selectedFormats: any[] = []
  let selectedParadigms: any[] = []
  let selectedTags: any[] = []

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
    valid_tags;
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
    parameters: '',
    valid_tags: []
  };

  // These should be fetched from your API or passed as props
    export let showModal = false;
    export let uniqueParadigms: any[] = [];
    export let uniqueFormats: any[] = [];
    export let uniqueFlows: any[] = [];
    export let uniqueCategories: string[] = [];
    export let tags: any[] = [];

  onMount(async () => {
    uniqueParadigms = uniqueParadigms.map((item: any) => ({ id: item._id, label: item.name }));
    uniqueFormats = uniqueFormats.map((item: any) => ({ id: item._id, label: item.name }));
  })

  async function handleSubmit() {
    try {
      console.log('New Analysis', newAnalysis);
      let baseResult = await getMatchingFiles(newAnalysis.valid_formats, newAnalysis.valid_paradigms);
      baseResult = baseResult.map((file: any) => file._id);
      if (newAnalysis.valid_tags.length > 0) {
        let taggedResult = await getMatchingTaggedFiles(newAnalysis.valid_tags);
        taggedResult = taggedResult.map((file: any) => file._id);
        newAnalysis.valid_files = [...baseResult, ...taggedResult];
      } else {
        newAnalysis.valid_files = baseResult;
      }

      if (newAnalysis.output_path === "") {
        newAnalysis.output_path = "./portal_files/output";
      }1

      await addAnalysis(newAnalysis);
      dispatch('showToast', { message: 'Analysis added successfully', type: 'success' });
      closeModal();
    } catch (error) {
      console.error('Error:', error);
      dispatch('showToast', { message: 'Error occurred', type: 'error' });
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
      parameters: '',
      valid_tags: []
    };
    selectedFormats = []
    selectedParadigms = []
    selectedTags = []
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
            <Input bind:value={newAnalysis.name} required class="w-full p-2 border rounded"/>
          </div>
          <div>
            <label for="analysis_flow" class="block text-md font-semibold text-gray-700 mb-1">Flow Name:</label>
            <Select.Root>
              <Select.Trigger>
                <Select.Value placeholder="Select Flow" />
              </Select.Trigger>
              <Select.Content>
                {#each uniqueFlows as analysisFlow}
                  <Select.Item value={analysisFlow._id} on:click={() => newAnalysis.analysis_flow = analysisFlow._id}>{analysisFlow.name}</Select.Item>
                {/each}
              </Select.Content>
            </Select.Root>
          </div>

          <div>
            <label for="valid_formats" class="block text-md font-semibold text-gray-700 mb-1">Valid Formats:</label>
            <MultiSelect 
                bind:selected = {selectedFormats} 
                options={uniqueFormats} 
                on:change={handleFormatSelection}
                required
            />
          </div>

          <div>
            <label for="valid_paradigms" class="block text-md font-semibold text-gray-700 mb-1">Valid Paradigms:</label>
            <MultiSelect 
                bind:selected = {selectedParadigms} 
                options={uniqueParadigms} 
                on:change={handleParadigmSelection}
                required
            />
          </div>
<!-- 
          <Tabs>
            <TabsList class="grid w-full grid-cols-2">
              <TabsTrigger value="text-white">
                <Tooltip.Root>
                  <Tooltip.Trigger >All</Tooltip.Trigger>
                  <Tooltip.Content>
                    <p>Files must match all of the selected Tags</p>
                  </Tooltip.Content>
                </Tooltip.Root>
              </TabsTrigger>
              <TabsTrigger value="text-white">
                <Tooltip.Root>
                  <Tooltip.Trigger>Any</Tooltip.Trigger>
                  <Tooltip.Content>
                    <p>Files must match one of the selected Tags</p>
                  </Tooltip.Content>
                </Tooltip.Root>
              </TabsTrigger>
            </TabsList>
          </Tabs> -->

          <div>
            <label for="tags" class="block text-md font-semibold text-gray-700 mb-1">Valid Tags:</label>
            <MultiSelect
              options={tags}
              bind:selected={newAnalysis.valid_tags}
            />
          </div>
          <div>
            <label for="output_path" class="block text-md font-semibold text-gray-700 mb-1">Output Path:</label>
            <Input 
              type="text" 
              id="output_path" 
              bind:value={newAnalysis.output_path}
              placeholder="Default: portal_files/output"
              class="w-full p-2 border rounded"
            />
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