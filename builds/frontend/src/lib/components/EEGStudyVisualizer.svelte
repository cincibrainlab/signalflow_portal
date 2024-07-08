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
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
  } from "$lib/components/ui/select"
  import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "$lib/components/ui/table"

  export let studyData: {
    study: any
    participants: any[]
    sessions: any[]
  }

  let selectedSession: any = null
  let filteredSessions: any[] = studyData.sessions
  let searchTerm = ""
  let selectedDiagnosis: string = "All"
  let selectedAgeGroup: string = "All"
  let selectedParadigm: string = "All"
  let viewMode: "card" | "table" = "card"

  let uniqueDiagnoses: string[] = []
  let uniqueAgeGroups: string[] = []
  let uniqueParadigms: string[] = []

  let sortColumn: string = ""
  let sortDirection: "asc" | "desc" = "asc"

  onMount(() => {
    uniqueDiagnoses = [
      "All",
      ...new Set(
        studyData.participants.map((p) => p.clinical_measures.diagnosis),
      ),
    ]
    uniqueAgeGroups = [
      "All",
      ...new Set(studyData.participants.map((p) => p.demographics.age_group)),
    ]
    uniqueParadigms = [
      "All",
      ...new Set(
        studyData.sessions.flatMap((s) => s.paradigms.map((p: any) => p.type)),
      ),
    ]
  })
  $: {
    console.log("Filtering sessions...")
    filteredSessions = studyData.sessions.filter((session) => {
      const participant = getParticipant(session.participant_id)
      console.log("Session:", session.eegid, "Participant:", participant)

      const matchesSearch =
        session.eegid.toLowerCase().includes(searchTerm.toLowerCase()) ||
        session.participant_id.toLowerCase().includes(searchTerm.toLowerCase())
      console.log("Matches search:", matchesSearch)

      const matchesDiagnosis =
        selectedDiagnosis === "All" ||
        participant?.clinical_measures.diagnosis === selectedDiagnosis
      console.log("Matches diagnosis:", matchesDiagnosis)

      const matchesAgeGroup =
        selectedAgeGroup === "All" ||
        participant?.demographics.age_group === selectedAgeGroup
      console.log("Matches age group:", matchesAgeGroup)

      const matchesParadigm =
        selectedParadigm === "All" ||
        session.paradigms.some((p: any) => p.type === selectedParadigm)
      console.log("Matches paradigm:", matchesParadigm)

      const result =
        matchesSearch && matchesDiagnosis && matchesAgeGroup && matchesParadigm
      console.log("Final result:", result)

      return result
    })
    console.log("Filtered sessions:", filteredSessions.length)

    if (sortColumn) {
      filteredSessions.sort((a, b) => {
        let aValue, bValue
        switch (sortColumn) {
          case "eegid":
          case "participant_id":
          case "equipment_used":
            aValue = a[sortColumn]
            bValue = b[sortColumn]
            break
          case "date":
            aValue = new Date(a.date)
            bValue = new Date(b.date)
            break
          case "diagnosis":
          case "age_group":
          case "species":
            const aParticipant = getParticipant(a.participant_id)
            const bParticipant = getParticipant(b.participant_id)
            if (sortColumn === "diagnosis") {
              aValue = aParticipant?.clinical_measures.diagnosis
              bValue = bParticipant?.clinical_measures.diagnosis
            } else {
              aValue = aParticipant?.demographics[sortColumn]
              bValue = bParticipant?.demographics[sortColumn]
            }
            break
          case "paradigms":
            aValue = a.paradigms.map((p: any) => p.type).join(",")
            bValue = b.paradigms.map((p: any) => p.type).join(",")
            break
        }
        if (aValue < bValue) return sortDirection === "asc" ? -1 : 1
        if (aValue > bValue) return sortDirection === "asc" ? 1 : -1
        return 0
      })
    }
  }

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

  function getParticipant(participantId: string) {
    return studyData.participants.find(
      (p) => p.participant_id === participantId,
    )
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
      {#each filteredSessions as session}
        {@const participant = getParticipant(session.participant_id)}
        <Card
          class="hover:shadow-lg transition-shadow duration-300 cursor-pointer"
          on:click={() =>
            (selectedSession = selectedSession === session ? null : session)}
        >
          <CardHeader>
            <CardTitle class="flex items-center justify-between">
              <span>EEGID: {session.eegid}</span>
              <div class="flex gap-2">
                <Badge
                  class={getDiagnosisBadgeClasses(
                    participant?.clinical_measures.diagnosis,
                  )}
                >
                  {participant?.clinical_measures.diagnosis || "Unknown"}
                </Badge>
                <Badge
                  class={getAgeBadgeClasses(
                    participant?.demographics.age_group,
                  )}
                >
                  <svelte:component
                    this={getAgeIcon(participant?.demographics.age_group)}
                    class="w-4 h-4 mr-1"
                  />
                  {participant?.demographics.age_group || "Unknown"}
                </Badge>
                <Badge variant="outline" class="flex items-center gap-1">
                  <svelte:component
                    this={getSpeciesIcon(participant?.demographics.species)}
                    class="w-4 h-4 mr-1"
                  />
                  {participant?.demographics.species || "Unknown"}
                </Badge>
              </div>
            </CardTitle>
            <CardDescription>
              Date: {new Date(session.date).toLocaleDateString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p class="text-sm text-gray-600">
              Participant ID: {session.participant_id}
            </p>
            <p class="text-sm text-gray-600">
              Equipment: {session.equipment_used}
            </p>
          </CardContent>
          <CardFooter class="flex justify-between">
            {#each session.paradigms as paradigm}
              <Badge variant="outline" class="flex items-center gap-1">
                <svelte:component
                  this={getParadigmIcon(paradigm.type)}
                  class="w-4 h-4"
                />
                {paradigm.type.replace("_", " ")}
              </Badge>
            {/each}
          </CardFooter>
          <CardFooter>
            <a
              href={getDetailedRecordLink(session.eegid)}
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
        {#each filteredSessions as session}
          {@const participant = getParticipant(session.participant_id)}
          <TableRow
            on:click={() =>
              (selectedSession = selectedSession === session ? null : session)}
            class="cursor-pointer hover:bg-gray-100"
          >
            <TableCell>{session.eegid}</TableCell>
            <TableCell>{session.participant_id}</TableCell>
            <TableCell>{new Date(session.date).toLocaleDateString()}</TableCell>
            <TableCell>
              <Badge
                class={getDiagnosisBadgeClasses(
                  participant?.clinical_measures.diagnosis,
                )}
              >
                {participant?.clinical_measures.diagnosis || "Unknown"}
              </Badge>
            </TableCell>
            <TableCell>
              <Badge
                class={getAgeBadgeClasses(participant?.demographics.age_group)}
              >
                <svelte:component
                  this={getAgeIcon(participant?.demographics.age_group)}
                  class="w-4 h-4 mr-1"
                />
                {participant?.demographics.age_group || "Unknown"}
              </Badge>
            </TableCell>
            <TableCell>
              <Badge variant="outline" class="flex items-center gap-1">
                <svelte:component
                  this={getSpeciesIcon(participant?.demographics.species)}
                  class="w-4 h-4 mr-1"
                />
                {participant?.demographics.species || "Unknown"}
              </Badge>
            </TableCell>
            <TableCell>{session.equipment_used}</TableCell>
            <TableCell>
              <div class="flex gap-1">
                {#each session.paradigms as paradigm}
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
                href={getDetailedRecordLink(session.eegid)}
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
  {#if selectedSession}
    <section
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
    >
      <dialog
        class="bg-white rounded-lg p-6 max-w-2xl w-full"
        transition:fade
        open
      >
        <div
          role="button"
          tabindex="0"
          on:click|self={() => (selectedSession = null)}
          on:keydown={(e) => e.key === "Escape" && (selectedSession = null)}
        >
          <h2 class="text-2xl font-bold mb-4">
            Session Details: {selectedSession.eegid}
          </h2>
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <h3 class="font-semibold">Session Info</h3>
              <p>Date: {new Date(selectedSession.date).toLocaleString()}</p>
              <p>Equipment: {selectedSession.equipment_used}</p>
              <p>Notes: {selectedSession.notes}</p>
            </div>
            <div>
              <h3 class="font-semibold">Participant Info</h3>
              {#if getParticipant(selectedSession.participant_id)}
                {@const participant = getParticipant(
                  selectedSession.participant_id,
                )}
                <p>Age: {participant.demographics.age}</p>
                <p>Age Group: {participant.demographics.age_group}</p>
                <p>Gender: {participant.demographics.gender}</p>
                <p>Handedness: {participant.demographics.handedness}</p>
                <p>Species: {participant.demographics.species}</p>
                <p>Diagnosis: {participant.clinical_measures.diagnosis}</p>
                <p>IQ Score: {participant.clinical_measures.iq_score}</p>
                <p>
                  Anxiety Level: {participant.clinical_measures.anxiety_level}
                </p>
              {/if}
            </div>
          </div>
          <div>
            <h3 class="font-semibold mb-2">Paradigms</h3>
            {#each selectedSession.paradigms as paradigm}
              <div class="mb-2 p-2 bg-gray-100 rounded">
                <h4 class="font-medium">{paradigm.type.replace("_", " ")}</h4>
                <p>Duration: {paradigm.duration} seconds</p>
                <p>File: {paradigm.file.filename}</p>
                <p>Status: {paradigm.file.processing_status}</p>
                {#if paradigm.metadata}
                  <p>Metadata: {JSON.stringify(paradigm.metadata)}</p>
                {/if}
              </div>
            {/each}
          </div>
          <Button class="mt-4" on:click={() => (selectedSession = null)}
            >Close</Button
          >
        </div>
      </dialog>
    </section>
  {/if}
</div>
