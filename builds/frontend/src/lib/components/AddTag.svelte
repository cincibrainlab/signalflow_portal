<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { Button } from "$lib/components/ui/button";
    import { Badge } from "$lib/components/ui/badge";
    import { Input } from "$lib/components/ui/input";
    import { addTag } from '$lib/services/apiService';
    import ColorPicker from 'svelte-awesome-color-picker';

    export let showModal = false;

    const dispatch = createEventDispatcher();

    let newTag = {
        name: '',
        color: '#000000',
        text_color: '#000000'
    };

    async function handleSubmit() {
        try {
            await addTag(newTag.name, newTag.color);
            dispatch('tagAdded', newTag);
            dispatch('toast', { message: 'Tag added successfully', type: 'success' });
            closeModal();
        } catch (error) {
            console.error('Error adding new tag:', error);
            dispatch('toast', { message: 'Error adding new tag', type: 'error' });
        }
    }

    function closeModal() {
        showModal = false;
        dispatch('close');
        // Reset the form
        newTag = {
            name: '',
            color: '#000000',
            text_color: '#000000'
        };
    }
</script>

{#if showModal}
    <section class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-20" role="dialog" aria-modal="true">
        <dialog class="bg-white rounded-lg p-6 max-w-md w-full overflow-auto h-auto" open>
            <h2 class="text-2xl font-bold mb-[20px]">Add New Tag</h2>
            <form on:submit|preventDefault={handleSubmit}>
                <div class="grid gap-4 mb-[40px]">
                    <div>
                        <label for="name" class="block text-base font-semibold text-gray-700 mb-1">Tag Name:</label>
                        <Input type="text" id="name" bind:value={newTag.name} required class="w-full p-2 border rounded" />
                    </div>
                    <label for="color" class="block text-base font-semibold text-gray-7000 mb-1">Tag Color:</label>
                    <div class="flex justify-center">
                        <ColorPicker bind:hex={newTag.color} isOpen={true} isPopup={false} canChangeMode={false} isInput={false} />
                    </div>
                    <div class="flex flex-wrap justify-center gap-2 mt-2">
                        <Badge class="text-black text-base" style="background-color: {newTag.color};">{newTag.name || "Example"}</Badge>
                    </div>
                </div>
                <div class="flex justify-between gap-2 mt-2">
                    <Button class="p-5" variant="outline" on:click={closeModal}>Cancel</Button>
                    <Button class="p-5" type="submit">Add Tag</Button>
                </div>
            </form>
        </dialog>
    </section>
{/if}