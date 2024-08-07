<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Button } from "$lib/components/ui/button";
  import { addParticipant, getFormOptions } from '$lib/services/apiService';


  export let showModal = false;
  export let uniqueGroups: string[] = [];
  export let uniqueAgeGroups: string[] = [];
  export let uniqueTypes: string[] = [];
  export let uniqueSexes: string[] = [];
  export let uniqueHandednesses: string[] = [];

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


  async function handleSubmit() {
    try {
      await addParticipant(newParticipant);
      dispatch('participantAdded', newParticipant);
      dispatch('toast', { message: 'Participant added successfully', type: 'success' });
      closeModal();
    } catch (error) {
      console.error('Error adding new participant:', error);
      dispatch('toast', { message: 'Error adding new participant', type: 'error' });
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

</script>

{#if showModal}
  <section class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-20" role="dialog" aria-modal="true">
    <dialog class="bg-white rounded-lg p-6 max-w-2xl w-full overflow-auto h-5/6" open>
      <h2 class="text-2xl font-bold mb-[20px]">Add New Participant</h2>
      <form on:submit|preventDefault={handleSubmit}>
        <span class="text-xl font-semibold text-gray-700">Participant Info</span>
        <div class="grid grid-cols-2 gap-4 mb-[50px] mt-[10px]">
          <div>
            <label for="participant_id" class="block text-sm font-semibold text-gray-700 mb-1">Participant ID:</label>
            <input type="text" id="participant_id" bind:value={newParticipant.participant_id} required class="w-full p-2 border rounded">
          </div>
          <div></div>
          <div>
            <label for="species" class="block text-sm font-semibold text-gray-700 mb-1">Type:</label>
            <select id="species" bind:value={newParticipant.species} required class="w-full p-2 border rounded">
              {#each uniqueTypes as type}
                <option value={type}>{type}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="diagnosis" class="block text-sm font-semibold text-gray-700 mb-1">Group:</label>
            <select id="diagnosis" bind:value={newParticipant.diagnosis} required class="w-full p-2 border rounded">
              {#each uniqueGroups as group}
                <option value={group}>{group}</option>
              {/each}
            </select>
          </div>
        </div>
        <span class="text-xl font-semibold text-gray-700">Clinical Measures</span>
        <div class="grid grid-cols-2 gap-4 mt-[10px]">
          <div>
            <label for="age" class="block text-sm font-semibold text-gray-700 mb-1">Age:</label>
            <input type="number" id="age" bind:value={newParticipant.age} required class="w-full p-2 border rounded">
          </div>
          <div>
            <label for="age_group" class="block text-sm font-semibold text-gray-700 mb-1">Age Group:</label>
            <select id="age_group" bind:value={newParticipant.age_group} required class="w-full p-2 border rounded">
              {#each uniqueAgeGroups as ageGroup}
                <option value={ageGroup}>{ageGroup}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="sex" class="block text-sm font-semibold text-gray-700 mb-1">Sex:</label>
            <select id="sex" bind:value={newParticipant.gender} required class="w-full p-2 border rounded">
              {#each uniqueSexes as sex}
                <option value={sex}>{sex}</option>
              {/each}
            </select>
          </div>
          <div>
            <label for="handedness" class="block text-sm font-semibold text-gray-700 mb-1">Handedness:</label>
            <select id="handedness" bind:value={newParticipant.handedness} class="w-full p-2 border rounded">
              {#each uniqueHandednesses as handedness}
                <option value={handedness}>{handedness}</option>
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
          <Button class="p-5" type="submit">Add Participant</Button>
        </div>
      </form>
    </dialog>
  </section>
{/if}