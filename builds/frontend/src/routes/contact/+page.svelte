<script lang="ts">
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import { sendContactMessage } from '$lib/services/apiService';

  let name = '';
  let email = '';
  let message = '';

  let successMessage = '';

  const handleSubmit = async (event: Event) => {
    event.preventDefault();

    const formData = {
      name,
      email,
      message,
    };

    try {
      const response = await sendContactMessage(formData);

      if (response.ok) {
        successMessage = 'Your message has been sent successfully!';
        name = '';
        email = '';
        message = '';
      } else {
        successMessage = 'Failed to send your message. Please try again later.';
      }
    } catch (error) {
      successMessage = 'An error occurred. Please try again later.';
    }
  };
</script>
  
  <main class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6">Contact Us</h1>
  
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div>
        <h2 class="text-xl font-semibold mb-4">Send us a message</h2>
        <form on:submit|preventDefault={handleSubmit} class="space-y-4">
          <div class="form-control">
            <label for="name" class="label">
              <span class="label-text">Name</span>
            </label>
            <input type="text" id="name" bind:value={name} class="input input-bordered" required />
          </div>
          <div class="form-control">
            <label for="email" class="label">
              <span class="label-text">Email</span>
            </label>
            <input type="email" id="email" bind:value={email} class="input input-bordered" required />
          </div>
          <div class="form-control">
            <label for="message" class="label">
              <span class="label-text">Message</span>
            </label>
            <textarea id="message" bind:value={message} class="textarea textarea-bordered h-24" required></textarea>
          </div>
          <button type="submit" class="btn btn-primary">Send Message</button>
        </form>
      </div>
  
      <div>
        <h2 class="text-xl font-semibold mb-4">Developer Contact Information</h2>
        <div class="space-y-2">
          <p><strong>Frontend Developer:</strong> john.doe@example.com</p>
          <p><strong>Backend Developer:</strong> jane.smith@example.com</p>
          <p><strong>UI/UX Designer:</strong> alex.johnson@example.com</p>
        </div>
        <h2 class="text-xl font-semibold mt-6 mb-4">Office Hours</h2>
        <p>Monday - Friday: 9:00 AM - 5:00 PM</p>
        <p>Saturday - Sunday: Closed</p>
      </div>
    </div>
    {#if successMessage}
      <p>{successMessage}</p>
    {/if}
  </main>