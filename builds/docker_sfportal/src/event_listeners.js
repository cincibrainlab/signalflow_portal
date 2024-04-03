// eventListeners.js
export const addEventListeners = (uppy) => {
    document.addEventListener('DOMContentLoaded', function() {
      document.getElementById('datasetName').placeholder = 'Dataset_' + Date.now();
    });
  
    document.getElementById('uploadForm').addEventListener('submit', function(event) {
      event.preventDefault(); // Prevent the form from submitting normally
  
      const formData = new FormData(this);
      const metadata = {};
  
      formData.forEach((value, key) => {
        metadata[key] = value;
      });
  
      uppy.setMeta(metadata);
      uppy.upload();
    });
  };