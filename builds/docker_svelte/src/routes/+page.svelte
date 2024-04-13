<script>
  let eegFormat = '';
  let eegParadigm = '';
  let emailAddress = '';
  let datasetSelection = '';
  let newDatasetName = '';
  let datasets = ['Dataset 1', 'Dataset 2']; // Example datasets, replace with dynamic loading
  
  const submitForm = async () => {
    // Here you would handle the form submission, e.g., sending data to your backend
    console.log({ eegFormat, eegParadigm, emailAddress, datasetSelection, newDatasetName });
  };

  const createDataset = async () => {
    if (datasets.includes(newDatasetName)) {
      alert('Dataset name already exists. Please choose a different name.');
    } else {
      // Here you would handle the creation of a new dataset, e.g., sending data to your backend
      datasets.push(newDatasetName); // Simulate adding the new dataset
      datasetSelection = newDatasetName; // Select the newly created dataset
      alert('Dataset created successfully.');
    }
  };
</script>

<style>
  .upload-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
    max-width: 600px;
    margin: auto;
    padding: 20px;
    border: 2px solid #007BFF;
    border-radius: 12px;
    background-color: #f9f9f9;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  h2 {
    font-family: 'Arial', sans-serif;
    font-size: 24px;
    font-weight: bold;
    color: #333;
    margin-bottom: 20px;
  }
  
  .form-row {
    display: flex;
    justify-content: space-between;
    gap: 10px;
  }
  
  input, select {
    flex: 1;
    padding: 12px;
    border: 2px solid #ccc;
    border-radius: 6px;
    font-size: 16px;
  }
  
  button {
    width: 100%;
    padding: 12px 20px;
    background-color: #007BFF;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
    text-transform: uppercase;
    transition: background-color 0.3s ease;
  }
  
  button:hover {
    background-color: #0056b3;
  }
</style>

<div class="upload-form">
  <h2>SignalFlowEeg Upload Portal</h2>
  <div class="form-row">
    <select bind:value={eegFormat}>
      <option value="" disabled>Select EEG Format</option>
      <option value="format1">Format 1</option>
      <option value="format2">Format 2</option>
    </select>
    
    <select bind:value={eegParadigm}>
      <option value="" disabled>Select EEG Paradigm</option>
      <option value="paradigm1">Paradigm 1</option>
      <option value="paradigm2">Paradigm 2</option>
    </select>
  </div>
  
  <div class="form-row">
    <select bind:value={datasetSelection}>
      <option value="" disabled>Select or Create Dataset</option>
      {#each datasets as dataset}
        <option value={dataset}>{dataset}</option>
      {/each}
      <option value="create_new">Create New Dataset</option>
    </select>
    {#if datasetSelection === 'create_new'}
      <input type="text" bind:value={newDatasetName} placeholder="New Dataset Name" />
      <button on:click={createDataset}>Create</button>
    {/if}
  </div>
  
  <input type="email" bind:value={emailAddress} placeholder="Email Address" />
  
  <button on:click={submitForm}>Submit</button>
</div>


