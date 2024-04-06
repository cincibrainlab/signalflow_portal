const { Pool } = require('pg');

const pool = new Pool({
  user: 'sfportal',
  password: 'sfportal',
  host: 'localhost',
  database: 'sfportal',
  port: 3002,
});

async function getFilenames() {
  const client = await pool.connect();
  try {
    const res = await client.query('SELECT filename FROM eeg_file_catalog');
    return res.rows; // Each row has a 'filename' property
  } finally {
    client.release();
  }
}

async function getDatasetNames() {
  const client = await pool.connect();
  try {
    const res = await client.query('SELECT DISTINCT dataset_name FROM eeg_file_catalog');
    return res.rows; // Each row has a 'dataset_name' property
  } finally {
    client.release();
  }
}

async function getEegFormats() {
  const client = await pool.connect();
  try {
    const res = await client.query('SELECT format_name, description FROM eeg_format');
    return res.rows;
  } finally {
    client.release();
  }
}


async function getDatasetFileCounts() {
  const client = await pool.connect();
  try {
    const res = await client.query(`
      SELECT 
        dataset_name,
        COUNT(*) AS file_count
      FROM 
        eeg_file_catalog
      WHERE 
        filename LIKE '%.set'
      GROUP BY 
        dataset_name
    `);
    return res.rows;
  } finally {
    client.release();
  }
}


module.exports = {
  getFilenames,
  getDatasetNames,
  getEegFormats
};

