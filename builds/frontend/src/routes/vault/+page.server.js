// src/routes/study-visualizer/+page.server.js
import { generateStudyData } from '$lib/server/dataGenerator';

export function load() {
  const studyData = generateStudyData(20); // Generate data for 20 participants
  return { studyData };
}