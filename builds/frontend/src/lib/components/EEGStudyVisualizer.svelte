<!-- src/lib/components/EEGStudyVisualizer.svelte -->
<script lang="ts">
  import { onMount } from "svelte"
  import { goto } from "$app/navigation"
  import { invalidate } from '$app/navigation';
  import { fade, slide } from "svelte/transition"
  import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
  } from "$lib/components/ui/card"
  import { Button } from "$lib/components/ui/button"
  import { Badge } from "$lib/components/ui/badge"
  import {
    Brain,
    Activity,
    Zap,
    Cog,
    Baby,
    User2,
    Filter,
    Grid,
    List,
    Rat as Mouse,
    Cat,
    Dog,
    Calculator as FileAnalytics,
    ExternalLink,
    ArrowUpDown,
  } from "lucide-svelte"
  import { Input } from "$lib/components/ui/input"
  import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "$lib/components/ui/table"
  import { DateInput } from 'date-picker-svelte'
  import { getOriginalFileCatalog, getParticipants, assignParticipantToFile, getParticipant, addParticipant} from '$lib/services/apiService';
  import AddParticipant from './AddParticipant.svelte';
  import AddAnalysis from "./AddAnalysis.svelte";
  import { debounce } from 'lodash-es';
  import { getFormats, getParadigms, getEEGFormat, getParadigm } from '$lib/services/apiService';
  

  let selectedFile: any = null
  let NewFile: boolean = false
  // On the change of selectedFile, we want to fetch the participant data
  let searchTerm = ""
  let debouncedSearchTerm = ""
  let selectedDiagnosis: string = "All"
  let selectedAgeGroup: string = "All"
  let selectedParadigm: string = "All"
  let viewMode: "card" | "table" = "card"

  let uniqueDiagnoses: string[] = []
  let uniqueAgeGroups: string[] = []
  let uniqueParadigms: string[] = []
  let UniqueFormats: string[] = []
  let UniqueEquipment: string[] = []
  let UniqueGender: string[] = []
  let UniqueHandedness: string[] = []
  let UniqueSpecies: string[] = []

  let UniqueParadigmTypes: string[] = []
  let UniqueProcessingStatus: string[] = []

  let sortColumn: string = ""
  let sortDirection: "asc" | "desc" = "asc"

  let isEditing = false
  let selectedEEGFormat: any;
  let selectedParadigmData: any;
  let selectedEEGFormat_Name: string = ""
  let selectedParadigmData_Name: string = ""

  async function getSelectedFileData() {
  if (selectedFile) {
    try {
      // Fetching data
      selectedParadigmData = await getParadigm(selectedFile.eeg_paradigm);
      selectedEEGFormat = await getEEGFormat(selectedFile.eeg_format);

      selectedEEGFormat_Name = selectedEEGFormat?.name;
      selectedParadigmData_Name = selectedParadigmData?.name;

      // Log updated values
      console.log("Selected File:", selectedFile);
      console.log("Selected Paradigm:", selectedParadigmData);
      console.log("Selected EEG Format:", selectedEEGFormat);
    } catch (error) {
      console.error('Error fetching data:', error);
      // Handle the error appropriately
    }
  }
}

$: if (selectedFile) {
  if (selectedFile.status === "NEW") {
    NewFile = true;
  } else {
    NewFile = false;
    getSelectedFileData();
  }
}
  
  let Selected_participant_id: string = ""
  $: if (NewFile) {
    console.log("New File")
    console.log(Participants)

  }
  
  function formatDateForInput(dateString: string) {
    return new Date(dateString); // Returns YYYY-MM-DDTHH:mm
  }
  let saveChanges = () => {
    // Save changes to the selected session and participant
    isEditing = false
  }
  let Files: any = []
  let Participants: any = []

  function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

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
            const setFiles = result.filter((file: any) => file.is_set_file === true);
            const filesWithObjects = await getObjectsInFiles(setFiles);
            Files = filesWithObjects;
            console.log("Files with Objects:", Files);
          })
          .catch(error => {
            console.error('Error fetching file catalog:', error);
              // Handle the error appropriately
          });
    })
  }

  onMount(() => {
    getOriginalFileCatalog()
          .then(async (result) => {
            const setFiles = result.filter((file: any) => file.is_set_file === true);
            const filesWithObjects = await getObjectsInFiles(setFiles);
            Files = filesWithObjects;
            console.log("Files with Objects:", Files);
          })
          .catch(error => {
            console.error('Error fetching file catalog:', error);
              // Handle the error appropriately
          });

    getParticipants()
        .then(result => {
            Participants = result;
        })
        .catch(error => {
            console.error('Error fetching participants:', error);
            // Handle the error appropriately
        });

      getParadigms()
        .then(result => {
            uniqueParadigms = result.map((item: any) => item.name);
        })
        .catch(error => {
            console.error('Error fetching participants:', error);
            // Handle the error appropriately
        });

    getFormats()
        .then(result => {
            UniqueFormats = result.map((item: any) => item.name);
        })
        .catch(error => {
            console.error('Error fetching participants:', error);
            // Handle the error appropriately
        });

    uniqueDiagnoses = [
      "All",
      "FXS",
      "ASD",
      "DD",
      "Control",
      "Blind",
    ]
    uniqueAgeGroups = [
      "All",
      "infant",
      "pediatric",
      "adult",
    ]
    UniqueProcessingStatus = [
      "All",
      "raw",
      "preprocessed",
      "analyzed",
      "other"
    ]
  })

  let filteredFiles: any = []
  let isFiltering = false;

  $: {
    isFiltering = true;
    filteredFiles = Files.filter((file: any) => {
      const participant = file.participantData;

      const matchesSearch =
        file.original_name.toLowerCase().includes(debouncedSearchTerm.toLowerCase()) ||
        participant?.participant_id.toLowerCase().includes(debouncedSearchTerm.toLowerCase());

      const matchesDiagnosis =
        selectedDiagnosis === "All" ||
        participant?.diagnosis === selectedDiagnosis;

      const matchesAgeGroup =
        selectedAgeGroup === "All" ||
        participant?.age_group === selectedAgeGroup;

      const matchesParadigm =
        selectedParadigm === "All" ||
        file.eeg_paradigm.some((p: any) => p.type === selectedParadigm);

      return matchesSearch && matchesDiagnosis && matchesAgeGroup && matchesParadigm;
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
  console.log("Filtered Files:", filteredFiles)

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

  function getParadigmIcon(type: string) {
    switch (type) {
      case "resting_state":
        return Brain
      case "chirp":
        return Activity
      case "cognitive_flexibility":
        return Cog
      default:
        return Zap
    }
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
      ["infant", "yellow"],
      ["pediatric", "green"],
      ["adult", "blue"],
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
    return ageGroup === "pediatric" || ageGroup === "infant" ? Baby : User2
  }

  function getSpeciesIcon(species: string) {
    if (!species) {
      return User2
    }
    switch (species.toLowerCase()) {
      case "mouse":
        return Mouse
      case "cat":
        return Cat
      case "dog":
        return Dog
      default:
        return User2
    }
  }

  function toggleViewMode() {
    viewMode = viewMode === "card" ? "table" : "card"
  }

  function getDetailedRecordLink(eegid: string) {
    return `/record-viz?recordId=${eegid}`
  }

  let showAddParticipantModal = false;
  let showAddAnalysisModal = false;

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

  const updateDebouncedSearch = debounce((value: any) => {
    debouncedSearchTerm = value;
  }, 300);

  $: {
    updateDebouncedSearch(searchTerm);
  }

  $: {
    if (sortColumn === "eegid") {
      console.log("Sorted files by EEGID:", filteredFiles.map((f: any) => f.original_name));
    }
  }
</script>
<div class="container mx-auto p-4">
  <div class="mb-6 bg-white p-4 rounded-lg shadow">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold flex items-center">
        <Filter class="w-5 h-5 mr-2" />
        Filters
      </h2>

      <AddParticipant 
        bind:showModal={showAddParticipantModal} 
        on:participantAdded={handleParticipantAdded} 
        on:close={() => showAddParticipantModal = false}
      />
      <Button variant="outline" on:click={() => showAddParticipantModal = true}>
        Add New Participant
      </Button>

      <AddAnalysis 
        bind:showModal={showAddAnalysisModal} 
        on:close={() => showAddAnalysisModal = false}
      />
      <Button variant="outline" on:click={() => showAddAnalysisModal = true}>
        Add New Analysis
      </Button>

      <Button
        on:click={toggleViewMode}
        variant="outline"
        class="flex items-center"
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
      </div>
    </div>
  </div>

  {#if viewMode === "card"}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each filteredFiles as file}
        {#await getParticipant(file.participant) then participant}
          <Card
            class="hover:shadow-lg transition-shadow duration-300 cursor-pointer"
            on:click={() =>
              (selectedFile = selectedFile === file ? null : file)}
          >
            <CardHeader>
              <CardTitle class="flex items-center justify-between">
                <span>Name: {file.original_name}</span>
                <div class="flex gap-2">
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
                  <Badge variant="outline" class="flex items-center gap-1">
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
            <!-- TODO Make this into showing something else -->
            <!-- <CardFooter class="flex justify-between">
              {#each file.paradigms as paradigm}
                <Badge variant="outline" class="flex items-center gap-1">
                  <svelte:component
                    this={getParadigmIcon(paradigm.type)}
                    class="w-4 h-4"
                  />
                  {paradigm.type.replace("_", " ")}
                </Badge>
              {/each}
            </CardFooter> -->
            <CardFooter>
              <a
                href={getDetailedRecordLink(file.eegid)}
                class="text-blue-500 hover:text-blue-700 flex items-center"
              >
                View Details
                <ExternalLink class="w-4 h-4 ml-1" />
              </a>
            </CardFooter>
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
          <TableHead class="w-1/8" on:click={() => toggleSort("participant_id")}>
            Participant ID
            <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
          </TableHead>
          <TableHead class="w-1/8" on:click={() => toggleSort("date")}>
            Date
            <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
          </TableHead>
          <TableHead class="w-1/8" on:click={() => toggleSort("diagnosis")}>
            Diagnosis
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
          <TableHead class="w-1/8" on:click={() => toggleSort("paradigms")}>
            Paradigms
            <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
          </TableHead>
          <TableHead class="w-1/8">Details</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {#if isFiltering}
          <TableRow>
            <TableCell colspan={9} class="text-center">Loading...</TableCell>
          </TableRow>
        {:else}
          {#each filteredFiles as file (file.original_name)}
            <TableRow class="table-row-transition">
              <TableCell>{file.original_name}</TableCell>
              <TableCell>{file.participantData?.participant_id}</TableCell>
              <TableCell>{new Date(file.date_added).toLocaleDateString()}</TableCell>
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
                <Badge variant="outline" class="flex items-center gap-1">
                  <svelte:component
                    this={getSpeciesIcon(file.participantData?.species)}
                    class="w-4 h-4 mr-1"
                  />
                  {file.participantData?.species || "Unknown"}
                </Badge>
              </TableCell>
              <TableCell>{file.equipment_used}</TableCell>
              <TableCell>
                <div class="flex gap-1">
                  <!-- TODO Re-activate or change this  -->
                  <!-- {#each file.paradigms as paradigm}
                    <Badge variant="outline" class="flex items-center gap-1">
                      <svelte:component
                        this={getParadigmIcon(paradigm.type)}
                        class="w-4 h-4"
                      />
                      {paradigm.type.replace("_", " ")}
                    </Badge>
                  {/each} -->
                </div>
              </TableCell>
              <TableCell>
                <a
                  href={getDetailedRecordLink(file.eegid)}
                  class="text-blue-500 hover:text-blue-700 flex items-center"
                >
                  View
                  <ExternalLink class="w-4 h-4 ml-1" />
                </a>
              </TableCell>
            </TableRow>
          {/each}
        {/if}
      </TableBody>
    </Table>
  {/if}
  {#if NewFile === false && selectedFile}
    <section class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
      <dialog class="bg-white rounded-lg p-6 max-w-2xl w-full overflow-auto h-5/6" transition:fade open>
        <h2 class="text-2xl font-bold mb-4">Session Details: {selectedFile.eegid}</h2>
        <form>
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <!-- TODO add sessions -->
              <h3 class="font-semibold">Session Info</h3>
              <div class="w-full">
                <label
                  for="Date"
                  class="block text-sm font-semibold text-gray-700 mb-1">Date:</label>
                <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{new Date(selectedFile.date_added).toLocaleDateString()}</p>
              </div>
              <div class="w-full">
                <label
                  for="Equipment"
                  class="block text-sm font-semibold text-gray-700 mb-1">Format:</label>
                <select class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" bind:value={selectedEEGFormat_Name} disabled={!isEditing}>
                  {#each UniqueFormats as format}
                    <option value={format}>{format}</option>
                  {/each}
                </select>
              </div>
              <div class="w-full">
                <label
                  for="Equipment"
                  class="block text-sm font-semibold text-gray-700 mb-1">Paradigm:</label>
                <select class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" bind:value={selectedParadigmData_Name} disabled={!isEditing}>
                  {#each uniqueParadigms as paradigm}
                    <option value={paradigm}>{paradigm}</option>
                  {/each}
                </select>
              </div>
              <div class="w-full h-4/6">
                <label
                  for="Notes"
                  class="block text-sm font-semibold text-gray-700 mb-1">Notes:</label>
                <p class="block text-sm font-medium text-gray-700 mb-1 w-full resize-none h-5/6">{selectedFile.notes}</p>
              </div>
            </div>
            <div>
              <h3 class="font-semibold">Participant Info</h3>
              {#await getParticipant(selectedFile.participant) then selectedParticipant}
                {#if selectedParticipant}
                  <div class="w-full">
                    <label
                      for="Age"
                      class="block text-sm font-semibold text-gray-700 mb-1">Age:</label>
                    <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.age}</p>
                  </div>
                  <div class="w-full">
                    <label
                      for="Age Group"
                      class="block text-sm font-semibold text-gray-700 mb-1">Age Group:</label>
                    <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.age_group}</p>
                  </div>
                  <div class="w-full">
                    <label
                      for="Gender"
                      class="block text-sm font-semibold text-gray-700 mb-1">Gender:</label>
                    <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.gender}</p>
                  </div>
                  <div class="w-full">
                    <label
                      for="Handedness"
                      class="block text-sm font-semibold text-gray-700 mb-1">Handedness:</label>
                    <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.handedness}</p>
                  </div>
                  <div class="w-full">
                    <label
                      for="Species"
                      class="block text-sm font-semibold text-gray-700 mb-1">Species:</label>
                    <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.species}</p>
                  </div>
                  <div class="w-full">
                    <label
                      for="Diagnosis"
                      class="block text-sm font-semibold text-gray-700 mb-1">Diagnosis:</label>
                    <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.diagnosis}</p>
                  </div>
                  <div class="w-full">
                    <label
                      for="IQ Score"
                      class="block text-sm font-semibold text-gray-700 mb-1">IQ Score:</label>
                    <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.iq_score}</p>
                  </div>
                  <div class="w-full">
                    <label
                      for="Anxiety Level"
                      class="block text-sm font-semibold text-gray-700 mb-1">Anxiety Level:</label>
                    <p class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto">{selectedParticipant.anxiety_level}</p>
                  </div>
                {/if}
              {/await}
            </div>
          </div>
          
          {#if !isEditing}
            <Button on:click={() => isEditing = true}>Make changes</Button>
          {:else}
            <Button on:click={saveChanges}>Save</Button>
          {/if}
          
          <Button on:click={() => selectedFile = null}>Close</Button>
        </form>
      </dialog>
    </section>
  {/if}
  {#if NewFile === true && selectedFile}
    <section class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
      <dialog class="bg-white rounded-lg p-6 max-w-2xl w-full overflow-auto h-5/6" transition:fade open>
        <h2 class="text-2xl font-bold mb-4">Select Participant</h2>
          <form>
            <div class="w-full">
              <label
                for="Participant"
                class="block text-sm font-semibold text-gray-700 mb-1">Participant:</label>
              <select class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" bind:value={Selected_participant_id} >
                {#each Participants as person}
                  <option value={person.participant_id}>{person.participant_id}</option>
                {/each}
              </select>
            </div>
            <Button on:click={() => { assignParticipantToFile(Selected_participant_id,selectedFile.upload_id); selectedFile = null; getSetFiles();}}>Close</Button>
          </form>
      </dialog>
    </section>
  {/if}
</div>
