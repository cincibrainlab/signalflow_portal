// Static imports
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const { getFilenames, getDatasetNames, getEegFormats } = await import('./db.cjs'); // Adjust the path as necessary

const app = express();

// Get the __dirname equivalent by using the URL of the current module
const __dirname = path.dirname(fileURLToPath(import.meta.url));

app.use(express.static(path.join(__dirname, '../dist')));

app.use((req, res, next) => {
  console.log(`Received request for ${req.method} ${req.path}`);
  next();
});

// Test API endpoint
app.get('/api/test', (req, res) => {
  res.json({ message: 'Test API endpoint is working!' });
});

// API endpoint to get filenames
app.get('/api/filenames', async (req, res) => {
  try {
    const filenames = await getFilenames();
    res.json(filenames);
  } catch (error) {
    console.error('Failed to fetch filenames:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/datasets', async (req, res) => {
  try {
    const datasetNames = await getDatasetNames();
    res.json(datasetNames);
  } catch (error) {
    console.error('Failed to fetch dataset names:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/eegformats', async (req, res) => {
  try {
    const names = await getEegFormats();
    res.json(names);
  } catch (error) {
    console.error('Failed to fetch dataset names:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Start the server
const port = 1234; // You can change the port number if needed
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});