// src/lib/db.js
import { MongoClient } from 'mongodb';
import { MONGODB_URI } from '$env/static/private';

if (!MONGODB_URI) {
    throw new Error('Please define the MONGODB_URI environment variable');
}

let client;
let clientPromise;

export async function getDb() {
    if (!client) {
        client = new MongoClient(MONGODB_URI);
        clientPromise = client.connect();
    }
    return (await clientPromise).db();
}

export async function start_mongo() {
    try {
        const db = await getDb();
        console.log('Connected to MongoDB');
        return db;
    } catch (e) {
        console.error('Error connecting to MongoDB:', e);
        throw e; // Re-throw the error instead of exiting the process
    }
}

// Add a default export
export default {
    getDb,
    start_mongo
};