<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Button } from "$lib/components/ui/button";
  import { getOriginalFileCatalog, getParticipants, assignParticipantToFile, getParticipant, addParticipant, getFormOptions} from '$lib/services/apiService';
  import { getFormats, getParadigms, getEEGFormat, getParadigm, assignEEGFormatToFile, assignEEGParadigmToFile } from '$lib/services/apiService';


  export let showModal = false;
  
  const dispatch = createEventDispatcher();

  let newParticipant = {
    participant_id: '',
    species: '',
    age: null,
    age_group: '',
    gender: '',
    handedness: '',
    diagnosis: '',
    iq_score: null,
    anxiety_level: null
  };

  // These should be fetched from your API or passed as props
  let UniqueGender = ["All", "male", "female", "non-binary/non-conforming", "other", "prefer not to respond"];
  let UniqueHandedness = ["All", "right", "left", "ambidextrous", "prefer not to respond"];
  let UniqueSpecies = ["All", "human", "mouse", "rat", "monkey", "dog", "cat", "Other"];
  let UniqueAgeGroups: string[]
  let UniqueDiagnoses: string[]

  async function handleSubmit() {
    try {
      console.log("Attempting to add: ", newParticipant)
      await addParticipant(newParticipant);
      dispatch('participantAdded', newParticipant);
      closeModal();
    } catch (error) {
      console.error('Error adding new participant:', error);
      // Handle error (e.g., show an error message to the user)
    }
  }

  function closeModal() {
    showModal = false;
    dispatch('close');
    // Reset the form
    newParticipant = {
      participant_id: '',
      age: null,
      age_group: '',
      gender: '',
      handedness: '',
      species: '',
      diagnosis: '',
      iq_score: null,
      anxiety_level: null
    };
  }

  onMount(() => {
      getFormOptions("Diagnosis")
        .then(result => {
          UniqueDiagnoses = result.form_options
        })
        .catch(error => {
            console.error('Error fetching diagnosies:', error);
            // Handle the error appropriately
        });

      getFormOptions("AgeGroup")
        .then(result => {
          UniqueAgeGroups = result.form_options
        })
        .catch(error => {
            console.error('Error fetching age groups:', error);
            // Handle the error appropriately
        });
  })
</script>

{#if showModal}
  <section class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-10" role="dialog" aria-modal="true">
    <dialog class="bg-white rounded-lg p-6 max-w-2xl w-full overflow-auto h-5/6" open>
      <h2 class="text-2xl font-bold mb-4">Add New Participant</h2>
      <form on:submit|preventDefault={handleSubmit}>
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label for="participant_id" class="block text-sm font-semibold text-gray-700 mb-1">Participant ID:</label>
            <input type="text" id="participant_id" bind:value={newParticipant.participant_id} required class="w-full p-2 border rounded">
          </div>
          <div>
            <label for="age" class="block text-sm font-semibold text-gray-700 mb-1">Age:</label>
            <input type="number" id="age" bind:value={newParticipant.age} required class="w-full p-2 border rounded">
          </div>
          <div>
            <label for="age_group" class="block text-sm font-semibold text-gray-700 mb-1">Age Group:</label>
            <select id="age_group" bind:value={newParticipant.age_group} required class="w-full p-2 border rounded">
              {#each UniqueAgeGroups as ageGroup}
                <option value={ageGroup}>{ageGroup}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="gender" class="block text-sm font-semibold text-gray-700 mb-1">Gender:</label>
            <select id="gender" bind:value={newParticipant.gender} required class="w-full p-2 border rounded">
              {#each UniqueGender as gender}
                <option value={gender}>{gender}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="handedness" class="block text-sm font-semibold text-gray-700 mb-1">Handedness:</label>
            <select id="handedness" bind:value={newParticipant.handedness} required class="w-full p-2 border rounded">
              {#each UniqueHandedness as handedness}
                <option value={handedness}>{handedness}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="species" class="block text-sm font-semibold text-gray-700 mb-1">Species:</label>
            <select id="species" bind:value={newParticipant.species} required class="w-full p-2 border rounded">
              {#each UniqueSpecies as species}
                <option value={species}>{species}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="diagnosis" class="block text-sm font-semibold text-gray-700 mb-1">Diagnosis:</label>
            <select id="diagnosis" bind:value={newParticipant.diagnosis} required class="w-full p-2 border rounded">
              {#each UniqueDiagnoses as diagnosis}
                <option value={diagnosis}>{diagnosis}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="iq_score" class="block text-sm font-semibold text-gray-700 mb-1">IQ Score:</label>
            <input type="number" id="iq_score" bind:value={newParticipant.iq_score} class="w-full p-2 border rounded">
          </div>
          <div>
            <label for="anxiety_level" class="block text-sm font-semibold text-gray-700 mb-1">Anxiety Level:</label>
            <input type="number" id="anxiety_level" bind:value={newParticipant.anxiety_level} class="w-full p-2 border rounded">
          </div>
        </div>
        <div class="absolute bottom-6 left-6 right-6 flex justify-between gap-2 mt-2">
          <Button class="p-5" variant="outline" on:click={closeModal}>Cancel</Button>
          <Button class="p-5" type="submit">Save Analysis</Button>
        </div>
      </form>
    </dialog>
  </section>
{/if}