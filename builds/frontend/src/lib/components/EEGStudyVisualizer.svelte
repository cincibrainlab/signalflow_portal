<!-- src/lib/components/EEGStudyVisualizer.svelte -->
<script lang="ts">
  // 1. Imports
  // Svelte/framework imports
  import { goto } from "$app/navigation";
  import { fade } from "svelte/transition";

  // Third-party library imports
  import { debounce } from 'lodash-es';

  // UI component imports
  import { Alert } from 'flowbite-svelte';
  import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Button } from "$lib/components/ui/button";
  import { Badge } from "$lib/components/ui/badge";
  import { Input } from "$lib/components/ui/input";
  import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "$lib/components/ui/table";
  import * as Select from "$lib/components/ui/select";
  import * as Sheet from "$lib/components/ui/sheet";
  import * as Pagination from "$lib/components/ui/pagination";
  import * as Tooltip from "$lib/components/ui/tooltip/index.js";
  import { ChevronLeft, ChevronRight } from "lucide-svelte";
  import MultiSelect from 'svelte-multiselect';

  // Icon imports
  import {
    Brain, Activity, Zap, Cog, Baby, UserRound, Filter, Grid, List,
    Rat as Mouse, ExternalLink, ArrowUpDown, X,
  } from "lucide-svelte";

  // Local component imports
  import AddParticipant from './AddParticipant.svelte';
  import AddTag from './AddTag.svelte';

  // Service imports
  import { 
    getOriginalFileCatalog, getParticipants, assignParticipantToFile, getParticipant,
    getEEGFormat, getParadigm, assignEEGFormatToFile, assignEEGParadigmToFile, assignTagsToFile, getTags 
  } from '$lib/services/apiService';
	import { cn } from "$lib/utils";

  // 2. Component props
  /** @type {import('./$types').PageData} */
  export let data;

  // 3. Reactive declarations
  $: filteredSelectedFiles = Files.filter((file: any) => selectedFiles.includes(file.original_name));

  $: {
    isFiltering = true;
    filteredFiles = Files.filter((file: any) => {
      const participant = file.participantData;

      const matchesSearch =
        file.original_name.toLowerCase().includes(debouncedSearchTerm.toLowerCase()) ||
        participant?.participant_id.toLowerCase().includes(debouncedSearchTerm.toLowerCase());

      const matchesGroup =
        selectedGroup === "All" ||
        participant?.diagnosis.toLowerCase() === selectedGroup.toLowerCase();

      const matchesAgeGroup =
        selectedAgeGroup === "All" ||
        participant?.age_group.toLowerCase() === selectedAgeGroup.toLowerCase();

      const matchesParadigm =
        selectedParadigm === "All" ||
        (file.paradigmData && file.paradigmData.name.toLowerCase() === selectedParadigm.toLowerCase());

      return matchesSearch && matchesGroup && matchesAgeGroup && matchesParadigm;
    }).sort((a: any, b: any) => {
      if (!sortColumn) return 0;
      
      let aValue, bValue;
      switch (sortColumn) {
        case "eegid":
          aValue = a.original_name;
          bValue = b.original_name;
          break;
        case "participant_id":
          aValue = a.participantData?.participant_id;
          bValue = b.participantData?.participant_id;
          break;
        case "equipment_used":
          aValue = a.equipment_used;
          bValue = b.equipment_used;
          break;
        case "date":
          aValue = new Date(a.date_added);
          bValue = new Date(b.date_added);
          break;
        case "diagnosis":
        case "age_group":
        case "species":
          aValue = a.participantData?.[sortColumn];
          bValue = b.participantData?.[sortColumn];
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

  $: {
    updateDebouncedSearch(searchTerm);
  }

  $: {
    if (sortColumn === "eegid") {
      console.log("Sorted files by EEGID:", filteredFiles.map((f: any) => f.original_name));
    }
  }

  // 4. State variables
  let {
    files: Files = [],
    participants: Participants = [],
    uniqueParadigms = ["All"],
    uniqueFormats: UniqueFormats = ["All"],
    uniqueAgeGroups = ["All"],
    uniqueGroups = ["All"],
    uniqueTypes = ["All"],
    uniqueSexes = ["All"],
    uniqueHandednesses = ["All"],
    tags: tags
  } = data;
  let selectedFile: any = null;
  let isEditing = false;
  let isBatchEditing = false;
  let editingFiles: any[] = [];
  let selectedEEGFormat_Name: string = "";
  let selectedParadigmData_Name: string = "";
  let Selected_participant_id: string = "";
  let selectedTags: string[] = [];
  let newTag: string = '';
  let searchTerm = "";
  let debouncedSearchTerm = "";
  let selectedGroup: string = "All";
  let selectedAgeGroup: string = "All";
  let selectedParadigm: string = "All";
  let viewMode: "card" | "table" = "table";
  let sortColumn: string = "";
  let sortDirection: "asc" | "desc" = "asc";
  let filteredFiles: any = [];
  let isFiltering = false;
  let selectedFiles: string[] = [];
  let showAddParticipantModal = false;
  let showAddTagModal = false;
  let toastMessage = '';
  let toastType: 'success' | 'error' = 'success';
  let showToast = false;
  let saveEdits = false;

  let currentPage = 1;
  let itemsPerPage = 10;

  $: totalPages = Math.ceil(filteredFiles.length / itemsPerPage);
  $: paginatedFiles = filteredFiles.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);
  console.log(filteredFiles)

  // 5. Lifecycle methods (if any)
  // onMount(() => { ... });

  // 6. Helper functions
  function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function getDiagnosisBadgeClasses(diagnosis: string): string {
    const colorMap = new Map([
      ["FXS", "red"],
      ["ASD", "purple"],
      ["DD", "orange"],
      ["Control", "green"],
      ["Blind", "blue"],
    ])

    const availableColors = ["red", "purple", "orange", "green", "blue"]
    let colorIndex = 0

    for (const [key, value] of colorMap.entries()) {
      if (!colorMap.has(diagnosis)) {
        colorMap.set(
          diagnosis,
          availableColors[colorIndex % availableColors.length],
        )
        colorIndex++
      }
    }

    const color = colorMap.get(diagnosis) || "gray"
    return `bg-${color}-500 text-white hover:bg-${color}-600`
  }

  function getAgeBadgeClasses(ageGroup: string): string {
    const colorMap = new Map([
      ["infant", "blue"],
      ["adolescent", "green"],
      ["adult", "yellow"],
    ])

    const availableColors = [
      "yellow",
      "green",
      "blue",
      "red",
      "purple",
      "orange",
    ]
    let colorIndex = 0

    if (!colorMap.has(ageGroup)) {
      while (
        Array.from(colorMap.values()).includes(availableColors[colorIndex])
      ) {
        colorIndex++
      }
      colorMap.set(
        ageGroup,
        availableColors[colorIndex % availableColors.length],
      )
    }

    const color = colorMap.get(ageGroup) || "gray"

    if (color === "yellow") {
      return `bg-${color}-300 text-black hover:bg-${color}-400`
    } else {
      return `bg-${color}-500 text-white hover:bg-${color}-600`
    }
  }

  function getAgeIcon(ageGroup: string) {
    return ageGroup === "pediatric" || ageGroup === "infant" ? Baby : UserRound
  }

  function getSpeciesIcon(species: string) {
    if (!species) {
      return UserRound
    }
    switch (species.toLowerCase()) {
      case "mouse":
        return Mouse
      default:
        return UserRound
    }
  }

  function handleTagAdded(event) {
  // Refresh your tags list here
    getTags()
      .then(result => {
        tags = result;
      })
      .catch(error => {
        console.error('Error fetching tags:', error);
        // Handle the error appropriately
      });
  }

  // 7. Event handlers
  function toggleEditing() {
    isEditing = !isEditing;
  }

  function toggleViewMode() {
    viewMode = viewMode === "card" ? "table" : "card";
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

  function toggleFileSelection(fileName: string) {
    selectedFiles = selectedFiles.includes(fileName)
      ? selectedFiles.filter(f => f !== fileName)
      : [...selectedFiles, fileName];
  }

  function handlePageChange(event: CustomEvent<number>) {
    currentPage = event.detail;
  }

  function handleToast(event: CustomEvent) {
    ({ message: toastMessage, type: toastType } = event.detail);
    showToast = true;
    setTimeout(() => showToast = false, 3000);
  }

  function handleParticipantAdded() {
    // Refresh your participants list here
    getParticipants()
    .then(result => {
            Participants = result;
        })
        .catch(error => {
            console.error('Error fetching participants:', error);
            // Handle the error appropriately
        });
  }

  function handleTagSelection(event) {
    selectedTags = event.detail;
  }

  // 8. Complex logic and data fetching
  async function getObjectsInFiles(files: any[]) {
    const filesWithObjects = await Promise.all(
      files.map(async (file) => {
        if (file.eeg_format) {
          const formatData = await getEEGFormat(file.eeg_format);
          file = { ...file, formatData };
        }
        if (file.participant) {
          const participantData = await getParticipant(file.participant);
          file = { ...file, participantData };
        }
        if (file.eeg_paradigm) {
          const paradigmData = await getParadigm(file.eeg_paradigm);
          file = { ...file, paradigmData };
        }
        return file;
      })
    );
    return filesWithObjects;
  }

  function getSetFiles() {
    sleep(500).then(() => { 
      Files = []
    
      getOriginalFileCatalog()
          .then(async (result) => {
            const setFiles = result.filter((file: any) => file.is_primary_file === true);
            const filesWithObjects = await getObjectsInFiles(setFiles);
            Files = filesWithObjects;
          })
          .catch(error => {
            console.error('Error fetching file catalog:', error);
              // Handle the error appropriately
          });
    })
  }

  function openDashboard(id: string) {
      goto(`/fileDashboard?id=${id}`);
  }

  function openFile(file: any) {
    selectedFile = file;
    selectedEEGFormat_Name = file.formatData?.name || "";
    selectedParadigmData_Name = file.paradigmData?.name || "";
    isEditing = false;
  }

  function openBatchEdit(files: any[]) {
    editingFiles = files;
    isBatchEditing = true;
    selectedFile = null;
    selectedEEGFormat_Name = "";
    selectedParadigmData_Name = "";
    Selected_participant_id = "";
    selectedTags = [];
  }

  function handleSheetOpenChange(open: boolean) {
    if (!open && saveEdits){
      if (selectedFile){
        saveChanges()
        console.log("saved changes")
      }
      else{
        saveBatchChanges()
        console.log("saved batch changes")
      }
    }
    else if (open) {
      if (filteredSelectedFiles.length === 1) {
        openFile(filteredSelectedFiles[0]);
      } else if (filteredSelectedFiles.length > 1) {
        openBatchEdit(filteredSelectedFiles);
      }
    }
    else {
      selectedFile = null;
      editingFiles = [];
      isBatchEditing = false;
      saveEdits = false;
    }
  }

  function saveChanges() {
    if (selectedFile) {
      if (selectedEEGFormat_Name) assignEEGFormatToFile(selectedEEGFormat_Name, selectedFile.upload_id);
      if (selectedParadigmData_Name) assignEEGParadigmToFile(selectedParadigmData_Name, selectedFile.upload_id);
      if (selectedTags.length > 0) assignTagsToFile(selectedTags, selectedFile.upload_id);
    }
    saveEdits = false;
    isEditing = false;
    selectedFile = null;
    selectedTags = [];
    getSetFiles();
  }

  function saveBatchChanges() {
    editingFiles.forEach(file => {
      if (selectedEEGFormat_Name) assignEEGFormatToFile(selectedEEGFormat_Name, file.upload_id);
      if (selectedParadigmData_Name) assignEEGParadigmToFile(selectedParadigmData_Name, file.upload_id);
      if (selectedTags.length > 0) assignTagsToFile(selectedTags, file.upload_id);
      assignParticipantToFile(Selected_participant_id, file.upload_id);
    });
    saveEdits = false;
    isBatchEditing = false;
    editingFiles = [];
    selectedTags = [];
    getSetFiles();
  }

  function SelectAllVisible(){
    selectedFiles = filteredFiles.map((f: any) => f.original_name);
  }
  function DeselectAll(){
    selectedFiles = [];
  }

  // 9. Exports (if any)
  // export function someExportedFunction() { ... }

  // Debounce function
  const updateDebouncedSearch = debounce((value: any) => {
    debouncedSearchTerm = value;
  }, 300);
</script>
<div class="container mx-auto p-4">
  {#if Files.length === 0}
    <div class="rounded-xl shadow-md p-6 text-center">
      <h2 class="text-2xl font-semibold mb-4 text-gray-700">No EEG Files Available</h2>
      <p class="mb-4">Sorry, there's nothing to display here yet. Start by uploading some EEG files.</p>
      <Button href="/upload" >Go to Upload Page</Button>
    </div>
  {:else}
    <div class="mb-6 p-4 rounded-lg shadow">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold flex items-center">
          <Filter class="w-5 h-5 mr-2" />
          Filters
        </h2>

        <AddParticipant 
          bind:showModal={showAddParticipantModal} 
          on:participantAdded={handleParticipantAdded}
          on:toast={handleToast}
          on:close={() => showAddParticipantModal = false}
          {uniqueGroups}
          {uniqueAgeGroups}
          {uniqueTypes}
          {uniqueSexes}
          {uniqueHandednesses}
        />
        <Button variant="outline" on:click={() => showAddParticipantModal = true}>
          Add New Participant
        </Button>

        <AddTag
          bind:showModal={showAddTagModal}
          on:tagAdded={handleTagAdded}
          on:toast={handleToast}
          on:close={() => showAddTagModal = false}
        />
        <Button variant="outline" on:click={() => showAddTagModal = true}>
          Add New Tag
        </Button>

        <Button
          on:click={toggleViewMode}
          
          class="flex items-center"
          variant="outline"
        >
          {#if viewMode === "card"}
            <List class="w-4 h-4 mr-2" />
            Switch to Table View
          {:else}
            <Grid class="w-4 h-4 mr-2" />
            Switch to Card View
          {/if}
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
            placeholder="Search by EEGID or Participant ID"
            bind:value={searchTerm}
          />
        </div>
        <div>
          <label
            for="group"
            class="block text-sm font-medium mb-1">Group</label
          >
          <Select.Root>
            <Select.Trigger class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 ">
              <Select.Value placeholder="All"/>
            </Select.Trigger>
            <Select.Content>
              {#each uniqueGroups as group}
                <Select.Item value={group} on:click={() => selectedGroup = group}>{group}</Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
        </div>
        <div>
          <label
            for="ageGroup"
            class="block text-sm font-medium mb-1">Age Group</label
          >
          <Select.Root>
            <Select.Trigger >
              <Select.Value placeholder="All" />
            </Select.Trigger>
            <Select.Content>
              {#each uniqueAgeGroups as ageGroup}
                <Select.Item value={ageGroup} on:click={() => selectedAgeGroup = ageGroup}>{ageGroup}</Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
        </div>
        <div>
          <label
            for="paradigm"
            class="block text-sm font-medium mb-1">Paradigm</label
          >
          <Select.Root >
            <Select.Trigger>
              <Select.Value placeholder="All" />
            </Select.Trigger>
            <Select.Content>
              {#each uniqueParadigms as paradigm}
                <Select.Item value={paradigm} on:click={() => selectedParadigm = paradigm}>{paradigm.replace("_", " ")}</Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
        </div>
        <span class="h-full align-middle flex items-center">Files Visible: {filteredFiles.length}</span>
      </div>
    </div> 
    <div class="mb-4 p-4 rounded-lg shadow max-h-36 overflow-y-scroll">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-xl font-semibold">Selected Files</h3>
        <div class="flex items-center gap-2">
          <Button
            class="w-full h-9 font-semibold rounded-md bg-blue-500 text-white hover:bg-blue-700"
            on:click={SelectAllVisible}
          >
            Select all  
          </Button>
          <Button
            class="w-full h-9 font-semibold rounded-md bg-blue-500 text-white hover:bg-blue-700"
            on:click={DeselectAll}
          >
            Deselect all 
          </Button>

          <Sheet.Root onOpenChange={handleSheetOpenChange}>
            <Sheet.Trigger >
              <Button>
                Make Changes
              </Button>
            </Sheet.Trigger>
            <Sheet.Content>
              {#key selectedFile || isBatchEditing}
                {#if selectedFile}
                  <Sheet.Header>
                    <Sheet.Title>File Details</Sheet.Title>
                    <Sheet.Description>
                      To make changes click "Edit" then click "Save Changes" to apply.
                    </Sheet.Description>
                  </Sheet.Header>
                  <div class="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <h3 class="font-semibold">Session Info</h3>
                      <div class="w-full">
                        <label for="Date" class="block text-sm font-semibold text-gray-700 mb-1">Date:</label>
                        <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{new Date(selectedFile.date_added).toLocaleDateString()}</p>
                      </div>
                      <div class="w-full">
                        <label for="Format" class="block text-sm font-semibold text-gray-700 mb-1">Format:</label>
                        <select class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" bind:value={selectedEEGFormat_Name} disabled={!isEditing}>
                          {#each UniqueFormats as format}
                            <option value={format}>{format}</option>
                          {/each}
                        </select>
                      </div>
                      <div class="w-full">
                        <label for="Paradigm" class="block text-sm font-semibold text-gray-700 mb-1">Paradigm:</label>
                        <select class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" bind:value={selectedParadigmData_Name} disabled={!isEditing}>
                          {#each uniqueParadigms as paradigm}
                            <option value={paradigm}>{paradigm}</option>
                          {/each}
                        </select>
                      </div>
                      <div class="w-full">
                        <label for="Tags" class="block text-sm font-semibold text-gray-7000 mb-1">Tags:</label>
                        <div class="flex flex-wrap gap-2">
                          {#if selectedFile.tags}
                            {#each selectedFile.tags as tag}
                              <Badge class="{tag.text_class}" style="background-color: {tag.color};">{tag.name}</Badge>
                            {/each}
                          {:else}
                            <p class="block text-sm font-medium text-gray-7000 mb-1 w-full h-auto">No tags assigned</p>
                          {/if}
                        </div>
                      </div>
                      <div class="w-full h-4/6">
                        <label for="Notes" class="block text-sm font-semibold text-gray-700 mb-1">Notes:</label>
                        <p class="block text-sm font-medium text-gray-700 mb-1 w-full resize-none h-5/6">{selectedFile.notes || ""}</p>
                      </div>
                    </div>
                    <div>
                      <h3 class="font-semibold">Participant Info</h3>
                      {#await getParticipant(selectedFile.participant) then selectedParticipant}
                        {#if selectedParticipant}
                          <div class="w-full">
                            <label for="Group" class="block text-sm font-semibold text-gray-700 mb-1">Group:</label>
                            <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.diagnosis}</p>
                          </div>
                          <div class="w-full">
                            <label for="Species" class="block text-sm font-semibold text-gray-700 mb-1">Type:</label>
                            <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.species}</p>
                          </div>
                          <div class="w-full">
                            <label for="Age" class="block text-sm font-semibold text-gray-700 mb-1">Age:</label>
                            <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.age || "n/a"}</p>
                          </div>
                          <div class="w-full">
                            <label for="Age Group" class="block text-sm font-semibold text-gray-700 mb-1">Age Group:</label>
                            <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.age_group || "n/a"}</p>
                          </div>
                          <div class="w-full">
                            <label for="Gender" class="block text-sm font-semibold text-gray-700 mb-1">Sex:</label>
                            <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.gender || "n/a"}</p>
                          </div>
                          <div class="w-full">
                            <label for="Handedness" class="block text-sm font-semibold text-gray-700 mb-1">Handedness:</label>
                            <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.handedness || "n/a"}</p>
                          </div>
                          <div class="w-full">
                            <label for="IQ Score" class="block text-sm font-semibold text-gray-700 mb-1">IQ Score:</label>
                            <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.iq_score || "n/a"}</p>
                          </div>
                          <div class="w-full">
                            <label for="Anxiety Level" class="block text-sm font-semibold text-gray-700 mb-1">Anxiety Level:</label>
                            <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.anxiety_level || "n/a"}</p>
                          </div>
                        {/if}
                      {/await}
                    </div>
                  </div>
                  {#if isEditing}
                  <div class="space-y-2">
                    <MultiSelect
                      options={tags}
                      bind:selected={selectedTags}
                      on:change={handleTagSelection}
                      placeholder="Select tags"
                      outerDivClass={cn(
                        "border-input ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring aria-[invalid]:border-destructive data-[placeholder]:[&>span]:text-muted-foreground flex h-9 w-full items-center justify-between whitespace-nowrap rounded-md border bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1",
                      )}
                      ulOptionsClass={cn(
                        "bg-popover text-popover-foreground relative z-50 min-w-[8rem] overflow-hidden rounded-md border shadow-md focus:outline-none",
                      )}
                      liOptionClass="relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                      liSelectedClass="bg-accent text-accent-foreground"
                    />
                  </div>
                  {/if}
                  <Sheet.Footer class="flex justify-end gap-2 mt-4">
                    <Sheet.Close>
                      <Button variant="outline">Close</Button>
                    </Sheet.Close>
                    <div>
                      {#if !isEditing}
                        <Button on:click={toggleEditing}>Edit</Button>
                      {:else}
                        <Button on:click={toggleEditing}>Cancel</Button>
                        <Sheet.Close>
                          <Button  on:click={() => saveEdits = true}>Save Changes</Button>
                        </Sheet.Close>
                      {/if}
                    </div>
                  </Sheet.Footer>
                {:else if isBatchEditing}
                  <Sheet.Header>
                    <Sheet.Title>Make Batch Changes</Sheet.Title>
                    <Sheet.Description>
                      Make changes to the selected files. Click "Save Changes" to apply the changes.
                    </Sheet.Description>
                  </Sheet.Header>
                  <form on:submit={saveBatchChanges}>
                    <div class="w-full mb-4">
                      <label for="Participant" class="block text-sm font-semibold text-gray-7000 mb-1">Participant:</label>
                      <Select.Root>
                        <Select.Trigger>
                          <Select.Value placeholder="Select a participant" />
                        </Select.Trigger>
                        <Select.Content>
                          {#each Participants as participant}
                            <Select.Item value={participant.participant_id} on:click={() => Selected_participant_id = participant.participant_id}>{participant.participant_id}</Select.Item>
                          {/each}
                        </Select.Content>
                      </Select.Root>
                    </div>
                    <div class="w-full mb-4">
                      <label for="Format" class="block text-sm font-semibold text-gray-700 mb-1">Format:</label>
                      <Select.Root>
                        <Select.Trigger>
                          <Select.Value placeholder="Select a format" />
                        </Select.Trigger>
                        <Select.Content>
                          {#each UniqueFormats as format}
                            <Select.Item value={format} on:click={() => selectedEEGFormat_Name = format}>{format}</Select.Item>
                          {/each}
                        </Select.Content>
                      </Select.Root>
                    </div>
                    <div class="w-full mb-4">
                      <label for="Paradigm" class="block text-sm font-semibold text-gray-700 mb-1">Paradigm:</label>
                      <Select.Root>
                        <Select.Trigger>
                          <Select.Value placeholder="Select a paradigm" />
                        </Select.Trigger>
                        <Select.Content>
                          {#each uniqueParadigms as paradigm}
                            <Select.Item value={paradigm} on:click={() => selectedParadigmData_Name = paradigm}>{paradigm}</Select.Item>
                          {/each}
                        </Select.Content>
                      </Select.Root>
                    </div>
                    <div class="space-y-2">
                      <div class="flex flex-wrap gap-2 justify-center mb-2">
                        {#each selectedTags as tag}
                          <Badge 
                            variant="secondary" 
                            class="flex items-center gap-1 {tag.text_class}"
                            style="background-color: {tag.color};"
                          >
                            {tag.label}
                          </Badge>
                        {/each}
                      </div>
                      <div class="space-y-2">
                        <MultiSelect
                          options={tags}
                          bind:selected={selectedTags}
                          on:change={handleTagSelection}
                          placeholder="Select tags"
                          outerDivClass={cn(
                            "border-input ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring aria-[invalid]:border-destructive data-[placeholder]:[&>span]:text-muted-foreground flex h-9 w-full items-center justify-between whitespace-nowrap rounded-md border bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1",
                          )}
                          ulOptionsClass={cn(
                            "bg-popover text-popover-foreground relative z-50 min-w-[8rem] overflow-hidden rounded-md border shadow-md focus:outline-none",
                          )}
                          liOptionClass="relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                          liSelectedClass="bg-accent text-accent-foreground"
                        />
                      </div>
                    </div>
                    <Sheet.Footer class="mt-4">
                      <Sheet.Close>
                        <Button variant="outline" type="button">Cancel</Button>
                        <Button type="submit"  on:click={() => saveEdits = true}>Save Changes</Button>
                      </Sheet.Close>
                    </Sheet.Footer>
                  </form>
                {:else}
                  <Sheet.Header>
                    <Sheet.Title>No Files Selected</Sheet.Title>
                    <Sheet.Description>
                      Please select one or more files to make changes.
                    </Sheet.Description>
                  </Sheet.Header>
                {/if}
              {/key}
            </Sheet.Content>
          </Sheet.Root>
        </div>
      </div>
      <ul>
        {#each selectedFiles as fileName}
          <li class="mb-2 flex items-center justify-between">
            <span>{fileName}</span>
            <button
              class="text-red-500 hover:text-red-700"
              on:click={() => toggleFileSelection(fileName)}
            >
              <X class="w-4 h-4" />
            </button>
          </li>
        {/each}
      </ul>
    </div>
    {#if viewMode === "card"}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each paginatedFiles as file}
          {#await getParticipant(file.participant) then participant}
            <Card
              class="hover:shadow-lg transition-shadow duration-300 relative cursor-pointer"
              on:click={() => toggleFileSelection(file.original_name)}
            >
              <div class="absolute top-2 right-2 z-10">
                <input
                  type="checkbox"
                  class="custom-checkbox appearance-none h-5 w-5 border border-gray-300 rounded-full checked:bg-green-500 checked:border-transparent focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                  checked={selectedFiles.includes(file.original_name)}
                  on:click={(event) => event.stopPropagation()}
                  on:change={() => toggleFileSelection(file.original_name)}
                />
              </div>
              <div class="overflow-hidden">
                <CardHeader>
                  <CardTitle class="flex items-center justify-between flex-wrap">
                    <Tooltip.Root>
                      <Tooltip.Trigger class="truncate max-w-80">{file.original_name}</Tooltip.Trigger>
                      <Tooltip.Content>
                        <p>{file.original_name}</p>
                      </Tooltip.Content>
                    </Tooltip.Root>
                    <div class="flex gap-2 flex-wrap">
                      <Badge
                        class={getDiagnosisBadgeClasses(
                          participant.diagnosis,
                        )}
                      >
                        {participant.diagnosis || "Unknown"}
                      </Badge>
                      <Badge
                        class={getAgeBadgeClasses(
                          participant?.age_group,
                        )}
                      >
                        <svelte:component
                          this={getAgeIcon(participant?.age_group)}
                          class="w-4 h-4 mr-1"
                        />
                        {participant?.age_group || "Unknown"}
                      </Badge>
                      <Badge  class="flex items-center gap-1">
                        <svelte:component
                          this={getSpeciesIcon(participant?.species)}
                          class="w-4 h-4 mr-1"
                        />
                        {participant?.species || "Unknown"}
                      </Badge>
                    </div>
                  </CardTitle>
                  <CardDescription>
                    Date: {new Date(file.date_added).toLocaleDateString()}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p class="text-sm text-gray-600">
                    Participant ID: {participant?.participant_id}
                  </p>
                  <p class="text-sm text-gray-600">
                    Status: {file.status}
                  </p>
                </CardContent>
                <CardFooter>
                  <Button
                    
                    class="text-blue-500 hover:text-blue-700 flex items-center"
                    variant="outline"
                    on:click={(event) => {
                      event.stopPropagation();
                      openDashboard(file.upload_id);
                    }}
                  >
                    View Details
                    <ExternalLink class="w-4 h-4 ml-1" />
                  </Button>
                </CardFooter>
              </div>
            </Card>
          {/await}
        {/each}
      </div>
    {:else}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead class="w-1/8" on:click={() => toggleSort("eegid")}>
              EEGID
              <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
            </TableHead>
            <TableHead class="w-1/8" on:click={() => toggleSort("paradigms")}>
              Paradigm
              <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
            </TableHead>
            <TableHead class="w-1/8" on:click={() => toggleSort("participant_id")}>
              Participant ID
              <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
            </TableHead>
            <TableHead class="w-1/8" on:click={() => toggleSort("diagnosis")}>
              Group
              <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
            </TableHead>
            <TableHead class="w-1/8" on:click={() => toggleSort("age_group")}>
              Age Group
              <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
            </TableHead>
            <TableHead class="w-1/8" on:click={() => toggleSort("species")}>
              Species
              <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
            </TableHead>
            <TableHead class="w-1/8" on:click={() => toggleSort("equipment_used")}>
              Equipment
              <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
            </TableHead>
            <TableHead class="w-1/8" on:click={() => toggleSort("date")}>
              Date
              <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
            </TableHead>
            <TableHead class="w-1/8">Details</TableHead>
            <TableHead class="w-[100px]">Select</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {#if isFiltering}
            <TableRow>
              <TableCell colspan={10} class="text-center">Loading...</TableCell>
            </TableRow>
          {:else}
            {#each paginatedFiles as file (file.original_name)}
              <TableRow 
                class="table-row-transition cursor-pointer"
                on:click={() => toggleFileSelection(file.original_name)}
              >
                <TableCell>
                  <Tooltip.Root>
                    <Tooltip.Trigger class="truncate max-w-72">{file.original_name}</Tooltip.Trigger>
                    <Tooltip.Content>
                      <p>{file.original_name}</p>
                    </Tooltip.Content>
                  </Tooltip.Root>
                </TableCell>
                <TableCell>{file.paradigmData?.name}</TableCell>
                <TableCell>{file.participantData?.participant_id}</TableCell>
                
                <TableCell>
                  <Badge
                    class={getDiagnosisBadgeClasses(
                      file.participantData?.diagnosis,
                    )}
                  >
                    {file.participantData?.diagnosis || "Unknown"}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge
                    class={getAgeBadgeClasses(file.participantData?.age_group)}
                  >
                    <svelte:component
                      this={getAgeIcon(file.participantData?.age_group)}
                      class="w-4 h-4 mr-1"
                    />
                    {file.participantData?.age_group || "Unknown"}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge  class="flex items-center gap-1">
                    <svelte:component
                      this={getSpeciesIcon(file.participantData?.species)}
                      class="w-4 h-4 mr-1"
                    />
                    {file.participantData?.species || "Unknown"}
                  </Badge>
                </TableCell>
                <TableCell>{file.formatData?.name}</TableCell>
                <TableCell>{new Date(file.date_added).toLocaleDateString()}</TableCell>
                <TableCell>
                  <Button
                    
                    class="text-blue-500 hover:text-blue-700 flex items-center"
                    variant="outline"
                    on:click={(event) => {
                      event.stopPropagation();
                      openDashboard(file.upload_id);
                    }}
                  >
                    View Details
                    <ExternalLink class="w-4 h-4 ml-1" />
                  </Button>
                </TableCell>
                <TableCell>
                  <input
                    type="checkbox"
                    class="custom-checkbox appearance-none h-5 w-5 border border-gray-300 rounded-full checked:bg-green-500 checked:border-transparent focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                    checked={selectedFiles.includes(file.original_name)}
                    on:click|stopPropagation
                    on:change={() => toggleFileSelection(file.original_name)}
                  />
                </TableCell>
              </TableRow>
            {/each}
          {/if}
        </TableBody>
      </Table>
    {/if}

    <div class="flex justify-between items-center mt-4">
      <div class="w-1/4">
        <!-- This empty div helps balance the layout -->
      </div>
      
      <Pagination.Root 
        count={filteredFiles.length} 
        perPage={itemsPerPage} 
        let:pages 
        let:currentPage
      >
        <Pagination.Content>
          <Pagination.Item>
            <Pagination.PrevButton on:click={() => currentPage > 1 && handlePageChange(new CustomEvent('change', { detail: currentPage - 1 }))}>
              <ChevronLeft class="h-4 w-4" />
              <span class="sr-only">Previous</span>
            </Pagination.PrevButton>
          </Pagination.Item>
          {#each pages as page (page.key)}
            {#if page.type === "ellipsis"}
              <Pagination.Item>
                <Pagination.Ellipsis />
              </Pagination.Item>
            {:else}
              <Pagination.Item>
                <Pagination.Link {page} isActive={currentPage === page.value} on:click={() => handlePageChange(new CustomEvent('change', { detail: page.value }))}>
                  {page.value}
                </Pagination.Link>
              </Pagination.Item>
            {/if}
          {/each}
          <Pagination.Item>
            <Pagination.NextButton on:click={() => currentPage < totalPages && handlePageChange(new CustomEvent('change', { detail: currentPage + 1 }))}>
              <span class="sr-only">Next</span>
              <ChevronRight class="h-4 w-4" />
            </Pagination.NextButton>
          </Pagination.Item>
        </Pagination.Content>
      </Pagination.Root>
    
      <div class="flex items-center space-x-2 w-1/4 justify-end">
        <span class="text-sm text-gray-700">Items per page:</span>
        <Button 
          variant={itemsPerPage === 10 ? "default" : "outline"} 
          size="sm" 
          on:click={() => {
            itemsPerPage = 10;
            currentPage = 1;
          }}
        >
          10
        </Button>
        <Button 
          variant={itemsPerPage === 20 ? "default" : "outline"} 
          size="sm" 
          on:click={() => {
            itemsPerPage = 20;
            currentPage = 1;
          }}
        >
          20
        </Button>
        <Button 
          variant={itemsPerPage === 30 ? "default" : "outline"} 
          size="sm" 
          on:click={() => {
            itemsPerPage = 30;
            currentPage = 1;
          }}
        >
          30
        </Button>
      </div>
    </div>
  {/if}
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

<style>
  .custom-checkbox:checked {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='%23fff'%3E%3Cpath fill-rule='evenodd' d='M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z' clip-rule='evenodd'/%3E%3C/svg%3E");
    background-size: 100% 100%;
    background-position: 50%;
    background-repeat: no-repeat;
  }
</style>