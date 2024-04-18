const { createUppyInstance } = require("./uppy_config.js");
const { addEventListeners } = require("./event_listeners.js");
// index.js
const uppy = createUppyInstance();
window.uppy = uppy;

uppy.on("complete", (result) => {
  if (result.failed.length === 0) {
    console.log("Upload successful");
  } else {
    console.warn("Upload failed with errors. See details below:");
    result.failed.forEach((file) => {
      console.error(`File: ${file.name}, Error: ${file.error}`);
    });
    alert("Some files failed to upload. Check the console for more details.");
  }

  console.log("successful files:", result.successful);
  if (result.failed.length > 0) {
    console.log("failed files:", result.failed.map(file => `${file.name} (Error: ${file.error})`));
  }
});
addEventListeners(uppy);

// async function populateDatasetDropdown() {
//   try {
//     const response = await fetch('/api/datasets');
//     if (!response.ok) {
//       throw new Error(`HTTP error ${response.status}`);
//     }
//     const datasetNames = await response.json();
//     console.log('Dataset names:', datasetNames);
//     // Rest of the code
//   } catch (error) {
//     console.error('Error fetching dataset names', error);
//   }
// }

// // Call the function to populate the dataset dropdown when the page loads
// populateDatasetDropdown();
