const { createUppyInstance } = require("./uppy_config.js");
const { addEventListeners } = require("./event_listeners.js");
// index.js
const uppy = createUppyInstance();
window.uppy = uppy;

uppy.on("complete", (result) => {
  if (result.failed.length === 0) {
    console.log("Upload successful");
  } else {
    console.warn("Upload failed");
  }

  console.log("successful files:", result.successful);
  console.log("failed files:", result.failed);
});

addEventListeners(uppy);

async function populateDatasetDropdown() {
  try {
    const response = await fetch('/api/datasets');
    const datasetNames = await response.json();
    console.log('Dataset names:', datasetNames);
    const dropdown = document.getElementById('existingDatasets');
    datasetNames.forEach(dataset => {
      const option = document.createElement('option');
      option.value = dataset.dataset_name; // Ensure this matches the property name in your API response
      option.textContent = dataset.dataset_name; // Same here
      dropdown.appendChild(option);
    });
  } catch (error) {
    console.error('Error fetching dataset names', error);
  }
}

window.addEventListener('load', async () => {
  try {
    const response = await fetch('/api/eegformats');
    const eegFormats = await response.json();
    console.log('EEG Types:', eegFormats);
    const dropdown = document.getElementById('eegDataType');

    // Add the new API results to the dropdown
    eegFormats.forEach(format => {
      const option = document.createElement('option');
      console.log('format', format.format_name);
      option.value = format.format_name;
      option.text = format.format_name;
      //option.attr('data-description', "format.description");

      //option.data('description') = format.description;
      //option.description = format.description;
      //option.setAttribute('description', `${format.format_name} - ${format.description}`);
      dropdown.appendChild(option);
    });
  } catch (error) {
    console.error('Error fetching EEG format names', error);
  }
});

// Call the function to populate the dataset dropdown when the page loads
populateDatasetDropdown();

//populateEegFormatDropDown();