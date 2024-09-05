<script lang="ts">
    import { onMount } from 'svelte';
    import { Badge, Input, Button, ColorPicker } from "$lib/components/ui";
    import { getTags, addTag, updateTagColor } from "$lib/services/apiService";
  
    let tags = [];
    let newTagName = "";
    let newTagColor = "#000000";
  
    onMount(async () => {
      tags = await getTags();
    });
  
    async function handleAddTag() {
      if (newTagName) {
        await addTag(newTagName, newTagColor);
        tags = [...tags, { label: newTagName, color: newTagColor }];
        newTagName = "";
        newTagColor = "#000000";
      }
    }
  
    async function handleUpdateColor(tag) {
      const result = await updateTagColor(tag.label, tag.color);
      if (result.success) {
        tags = tags.map(t => t.label === tag.label ? {...t, color: tag.color} : t);
      }
    }
  </script>
  
  <div class="tag-manager">
    <h2>Manage Tags</h2>
    
    <div class="new-tag-form">
      <Input bind:value={newTagName} placeholder="New tag name" />
      <ColorPicker bind:value={newTagColor} />
      <Button on:click={handleAddTag}>Add Tag</Button>
    </div>
  
    <div class="tag-list">
      {#each tags as tag}
        <div class="tag-item">
          <Badge style="background-color: {tag.color};">{tag.label}</Badge>
          <ColorPicker 
            bind:value={tag.color} 
            on:change={() => handleUpdateColor(tag)}
          />
        </div>
      {/each}
    </div>
  </div>
  
  <style>
    .tag-manager {
      /* Add your styles */
    }
    .new-tag-form, .tag-list, .tag-item {
      /* Add your styles */
    }
  </style>