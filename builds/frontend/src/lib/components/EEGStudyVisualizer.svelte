<!-- src/lib/components/EEGStudyVisualizer.svelte -->
<script lang="ts">
  import { onMount } from "svelte"
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
  import { getOriginalFileCatalog } from '$lib/services/apiService';

  let selectedFile: any = null
  // On the change of selectedFile, we want to fetch the participant data
  let searchTerm = ""
  let selectedDiagnosis: string = "All"
  let selectedAgeGroup: string = "All"
  let selectedParadigm: string = "All"
  let viewMode: "card" | "table" = "card"

  let uniqueDiagnoses: string[] = []
  let uniqueAgeGroups: string[] = []
  let uniqueParadigms: string[] = []
  let UniqueEquipment: string[] = []
  let UniqueGender: string[] = []
  let UniqueHandedness: string[] = []
  let UniqueSpecies: string[] = []

  let UniqueParadigmTypes: string[] = []
  let UniqueProcessingStatus: string[] = []

  let sortColumn: string = ""
  let sortDirection: "asc" | "desc" = "asc"

  let isEditing = false
  let selectedParticipant: any = null
  let selectedFileDate: any = null
  $: if (selectedFile) {
    selectedParticipant = {
      participant_id: "Unknown",
      age: -1,
      age_group: "All",
      gender: "All",
      handedness: "All",
      species: "All",
      diagnosis: "All",
      iq_score: -1,
      anxiety_level: -1,
    }
    // try {
    //   selectedParticipant = selectedFile.participant
    // } catch (e) {
    //     selectedParticipant = {
    //       participant_id: "Unknown",
    //       age: -1,
    //       age_group: "All",
    //       gender: "All",
    //       handedness: "All",
    //       species: "All",
    //       diagnosis: "All",
    //       iq_score: -1,
    //       anxiety_level: -1,
    //     }
    //     // Handle the case when selectedFile.participant is undefined
    //     // Add your exception handling code here
    // }
      selectedFile = formatDateForInput(selectedFile.date_added);
      console.log(selectedFile.date_added);
      console.log(selectedFile);
    }
  
  function formatDateForInput(dateString: string) {
    return new Date(dateString); // Returns YYYY-MM-DDTHH:mm
  }
  let saveChanges = () => {
    // Save changes to the selected session and participant
    isEditing = false
  }
  let Files: any = []

  onMount(() => {
    
    getOriginalFileCatalog().then(result => {
      Files = result;
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
    uniqueParadigms = [
      "All",
      "resting_state",
      "chirp",
      "cognitive_flexibility",
      "other",
    ]
    UniqueEquipment = [
      "All",
      "EGI Hydrocel 128 infant",
      "BioSemi ActiveTwo 32 infant",
      "EGI Hydrocel 128",
      "BrainVision 64",
      "EGI Hydrocel 32",
      "MCS 60-channel MEA",
      "Axion Maestro 768-channel MEA",
      "Neuropixels probe",
      "NeuroNexus silicon probe",
      "MultiChannel Systems MEA2100",
      "Alpha MED Scientific MED64",
      "NEURON simulation environment",
      "Unknown equipment"
    ]
    UniqueGender = [
      "All",
      "male",
      "female",
      "non-binary/non-conforming",
      "other",
      "prefer not to respond"
    ]
    UniqueHandedness = [
      "All",
      "right",
      "left",
      "ambidextrous",
      "prefer not to respond"
    ]
    UniqueSpecies = [
      "All",
      "Human",
      "Mouse",
      "Rat",
      "Monkey",
      "Dog",
      "Cat",
      "Other"
    ]
    UniqueParadigmTypes = [
      "All",
      "rest",
      "chirp",
      "cogflex",
      "revlearn",
      "statlearn",
      "alphabeats",
      "other"
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
  $:{
  filteredFiles = Files
  console.log("Filtered files:", filteredFiles)
  }
  // $: {
  //   // console.log("Filtering sessions...")
  //   let filteredFiles = Files.filter((file: any) => {
  //     const participant = file.participant

  //     const matchesSearch =
  //       file.eegid.toLowerCase().includes(searchTerm.toLowerCase()) ||
  //       file.participant.participant_id.toLowerCase().includes(searchTerm.toLowerCase())
  //     // console.log("Matches search:", matchesSearch)

  //     const matchesDiagnosis =
  //       selectedDiagnosis === "All" ||
  //       participant?.diagnosis === selectedDiagnosis
  //     // console.log("Matches diagnosis:", matchesDiagnosis)

  //     const matchesAgeGroup =
  //       selectedAgeGroup === "All" ||
  //       participant?.age_group === selectedAgeGroup
  //     // console.log("Matches age group:", matchesAgeGroup)

  //     const matchesParadigm =
  //       selectedParadigm === "All" ||
  //       file.eeg_paradigm.name.some((p: any) => p.type === selectedParadigm)
  //     // console.log("Matches paradigm:", matchesParadigm)

  //     const result =
  //       matchesSearch && matchesDiagnosis && matchesAgeGroup && matchesParadigm
  //     // console.log("Final result:", result)

  //     return result
  //   })

  //   if (sortColumn) {
  //     filteredFiles.sort((a:any, b: any) => {
  //       let aValue, bValue
  //       switch (sortColumn) {
  //         case "eegid":
  //         case "participant_id":
  //         case "equipment_used":
  //           aValue = a[sortColumn]
  //           bValue = b[sortColumn]
  //           break
  //         case "date":
  //           aValue = new Date(a.date_added)
  //           bValue = new Date(b.date_added)
  //           break
  //         case "diagnosis":
  //         case "age_group":
  //         case "species":
  //           const aParticipant = a.participant
  //           const bParticipant = b.participant
  //           if (sortColumn === "diagnosis") {
  //             aValue = aParticipant?.diagnosis
  //             bValue = bParticipant?.diagnosis
  //           } else {
  //             aValue = aParticipant?[sortColumn]
  //             bValue = bParticipant?[sortColumn]
  //           }
  //           break
  //         case "paradigms":
  //           aValue = a.paradigms.map((p: any) => p.type).join(",")
  //           bValue = b.paradigms.map((p: any) => p.type).join(",")
  //           break
  //       }
  //       if (aValue < bValue) return sortDirection === "asc" ? -1 : 1
  //       if (aValue > bValue) return sortDirection === "asc" ? 1 : -1
  //       return 0
  //     })
  //   }
  // }

  function toggleSort(column: string) {
    if (sortColumn === column) {
      sortDirection = sortDirection === "asc" ? "desc" : "asc"
    } else {
      sortColumn = column
      sortDirection = "asc"
    }
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
</script>

<div class="container mx-auto p-4">
  <div class="mb-6 bg-white p-4 rounded-lg shadow">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold flex items-center">
        <Filter class="w-5 h-5 mr-2" />
        Filters
      </h2>
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
        {@const participant = file.participant}
        <Card
          class="hover:shadow-lg transition-shadow duration-300 cursor-pointer"
          on:click={() =>
            (selectedFile = selectedFile === file ? null : file)}
        >
          <CardHeader>
            <CardTitle class="flex items-center justify-between">
              <span>EEGID: {file.eegid}</span>
              <div class="flex gap-2">
                <Badge
                  class={getDiagnosisBadgeClasses(
                    participant?.diagnosis,
                  )}
                >
                  {participant?.diagnosis || "Unknown"}
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
              Participant ID: {file.participant.participant_id}
            </p>
            <p class="text-sm text-gray-600">
              Equipment: {file.equipment_used}
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
      {/each}
    </div>
  {:else}
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead
            class="cursor-pointer"
            on:click={() => toggleSort("eegid")}
          >
            EEGID
            <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
          </TableHead>
          <TableHead
            class="cursor-pointer"
            on:click={() => toggleSort("participant_id")}
          >
            Participant ID
            <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
          </TableHead>
          <TableHead class="cursor-pointer" on:click={() => toggleSort("date")}>
            Date
            <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
          </TableHead>
          <TableHead
            class="cursor-pointer"
            on:click={() => toggleSort("diagnosis")}
          >
            Diagnosis
            <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
          </TableHead>
          <TableHead
            class="cursor-pointer"
            on:click={() => toggleSort("age_group")}
          >
            Age Group
            <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
          </TableHead>
          <TableHead
            class="cursor-pointer"
            on:click={() => toggleSort("species")}
          >
            Species
            <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
          </TableHead>
          <TableHead
            class="cursor-pointer"
            on:click={() => toggleSort("equipment_used")}
          >
            Equipment
            <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
          </TableHead>
          <TableHead
            class="cursor-pointer"
            on:click={() => toggleSort("paradigms")}
          >
            Paradigms
            <ArrowUpDown class="ml-2 h-4 w-4 inline-block" />
          </TableHead>
          <TableHead>Details</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {#each filteredFiles as file}
          {@const participant = file.participant.participant_id}
          <TableRow
            on:click={() =>
              (selectedFile = selectedFile === file ? null : file)}
            class="cursor-pointer hover:bg-gray-100"
          >
            <TableCell>{file.eegid}</TableCell>
            <TableCell>{file.participant.participant_id}</TableCell>
            <TableCell>{new Date(file.date_added).toLocaleDateString()}</TableCell>
            <TableCell>
              <Badge
                class={getDiagnosisBadgeClasses(
                  participant?.diagnosis,
                )}
              >
                {participant?.diagnosis || "Unknown"}
              </Badge>
            </TableCell>
            <TableCell>
              <Badge
                class={getAgeBadgeClasses(participant?.age_group)}
              >
                <svelte:component
                  this={getAgeIcon(participant?.age_group)}
                  class="w-4 h-4 mr-1"
                />
                {participant?.age_group || "Unknown"}
              </Badge>
            </TableCell>
            <TableCell>
              <Badge variant="outline" class="flex items-center gap-1">
                <svelte:component
                  this={getSpeciesIcon(participant?.species)}
                  class="w-4 h-4 mr-1"
                />
                {participant?.species || "Unknown"}
              </Badge>
            </TableCell>
            <TableCell>{file.equipment_used}</TableCell>
            <TableCell>
              <div class="flex gap-1">
                {#each file.paradigms as paradigm}
                  <Badge variant="outline" class="flex items-center gap-1">
                    <svelte:component
                      this={getParadigmIcon(paradigm.type)}
                      class="w-4 h-4"
                    />
                    {paradigm.type.replace("_", " ")}
                  </Badge>
                {/each}
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
      </TableBody>
    </Table>
  {/if}
  {#if selectedFile}
    <section class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
      <dialog class="bg-white rounded-lg p-6 max-w-2xl w-full overflow-auto h-5/6" transition:fade open>
        <h2 class="text-2xl font-bold mb-4">Session Details: {selectedFile.eegid}</h2>
        
        <form>
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <h3 class="font-semibold">Session Info</h3>
              <div class="w-full">
                <label
                  for="Date"
                  class="block text-sm font-semibold text-gray-700 mb-1">Date:</label>
                <DateInput value={selectedFileDate} format="MM-dd-yyyy" disabled={!isEditing}/>
              </div>
              <div class="w-full">
                <label
                  for="Equipment"
                  class="block text-sm font-semibold text-gray-700 mb-1">Equipment:</label>
                  <select class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" bind:value={selectedFile.equipment_used} disabled={!isEditing}>
                    {#each UniqueEquipment as equipment}
                      <option value={equipment}>{equipment}</option>
                    {/each}
                  </select>
              </div>
              <div class="w-full h-4/6">
                <label
                  for="Notes"
                  class="block text-sm font-semibold text-gray-700 mb-1">Notes:</label>
                <textarea class="block text-sm font-medium text-gray-700 mb-1 w-full resize-none h-5/6" bind:value={selectedFile.notes} disabled={!isEditing}></textarea>
              </div>
            </div>
            <div>
              <h3 class="font-semibold">Participant Info</h3>
              {#if selectedParticipant.participant_id}
                <div class="w-full">
                  <label
                    for="Age"
                    class="block text-sm font-semibold text-gray-700 mb-1">Age:</label>
                  <input class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" type="number" bind:value={selectedParticipant.age} disabled={!isEditing}>
                </div>
                <div class="w-full">
                  <label
                    for="Age Group"
                    class="block text-sm font-semibold text-gray-700 mb-1">Age Group:</label>
                  <select class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" bind:value={selectedParticipant.age_group} disabled={!isEditing}>
                    {#each uniqueAgeGroups as ageGroup}
                      <option value={ageGroup}>{ageGroup}</option>
                    {/each}
                  </select>
                </div>
                <div class="w-full">
                  <label
                    for="Gender"
                    class="block text-sm font-semibold text-gray-700 mb-1">Gender:</label>
                  <select class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" bind:value={selectedParticipant.gender} disabled={!isEditing}>
                    {#each UniqueGender as gender}
                      <option value={gender}>{gender}</option>
                    {/each}
                  </select>
                </div>
                <div class="w-full">
                  <label
                    for="Handedness"
                    class="block text-sm font-semibold text-gray-700 mb-1">Handedness:</label>
                  <select class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" bind:value={selectedParticipant.handedness} disabled={!isEditing}>
                    {#each UniqueHandedness as handedness}
                      <option value={handedness}>{handedness}</option>
                    {/each}
                  </select>
                </div>
                <div class="w-full">
                  <label
                    for="Species"
                    class="block text-sm font-semibold text-gray-700 mb-1">Species:</label>
                  <select class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" bind:value={selectedParticipant.species} disabled={!isEditing}>
                    {#each UniqueSpecies as species}
                      <option value={species}>{species}</option>
                    {/each}
                  </select>
                </div>
                <div class="w-full">
                  <label
                    for="Diagnosis"
                    class="block text-sm font-semibold text-gray-700 mb-1">Diagnosis:</label>
                  <input class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" type="text" bind:value={selectedParticipant.diagnosis} disabled={!isEditing}>
                </div>
                <div class="w-full">
                  <label
                    for="IQ Score"
                    class="block text-sm font-semibold text-gray-700 mb-1">IQ Score:</label>
                  <input class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" type="number" bind:value={selectedParticipant.iq_score} disabled={!isEditing}>
                </div>
                <div class="w-full">
                  <label
                    for="Anxiety Level"
                    class="block text-sm font-semibold text-gray-700 mb-1">Anxiety Level:</label>
                  <input class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" type="number" bind:value={selectedParticipant.anxiety_level} disabled={!isEditing}>
                </div>
              {/if}
            </div>
          </div>
          <div>
            <h3 class="font-semibold mb-2">Paradigms</h3>
            <!-- {#each selectedFile.paradigms as paradigm}
              <div class="mb-2 p-2 bg-gray-100 rounded">
                <div class="w-full">
                  <label
                    for="Paradigm Type"
                    class="block text-sm font-semibold text-gray-700 mb-1">Type:</label>
                  <select class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" bind:value={paradigm.type} disabled={!isEditing}>
                    {#each UniqueParadigmTypes as paradigmType}
                      <option value={paradigmType}>{paradigmType}</option>
                    {/each}
                  </select>
                </div> 
                <div class="w-full">
                  <label
                    for="Duration"
                    class="block text-sm font-semibold text-gray-700 mb-1">Duration:</label>
                  <input class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" type="number" bind:value={paradigm.duration} disabled={!isEditing}>
                </div>
                <div class="w-full">
                  <label
                    for="File"
                    class="block text-sm font-semibold text-gray-700 mb-1">File:</label>
                  <input class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" type="text" bind:value={paradigm.file.filename} disabled={!isEditing}>
                  <label
                    for="Processing Status"
                    class="block text-sm font-semibold text-gray-700 mb-1">Processing Status:</label>
                  <select class="block text-sm font-medium text-gray-700 mb-1 w-full h-auto" bind:value={paradigm.file.processing_status} disabled={!isEditing}>
                    {#each UniqueProcessingStatus as processingStatus}
                      <option value={processingStatus}>{processingStatus}</option>
                    {/each}
                  </select>
                  {#if paradigm.metadata}
                    <label for="Metadata" class="block text-sm font-semibold text-gray-700 mb-1">Metadata:</label>
                    <p>Metadata: {JSON.stringify(paradigm.metadata)}</p>
                  {/if}
                </div>
              </div>
            {/each} -->
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
</div>
