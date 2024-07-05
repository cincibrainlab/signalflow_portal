// src/lib/server/dataGenerator.ts
import { faker } from "@faker-js/faker"
// import { ObjectId } from 'mongodb';
import { getDb } from "$lib/db"
import type { Db } from "mongodb"
import { v4 as uuidv4 } from "uuid"

export interface Participant {
  _id: string
  participant_id: string
  demographics: {
    species: string
    age: number
    age_group: string
    gender: string
    handedness: string
  }
  clinical_measures: {
    diagnosis: string
    iq_score: number | null
    anxiety_level: number | null
  }
  study_ids: string[]
  recording_type: string
}

export interface Session {
  _id: string
  eegid: string
  session_id: string
  participant_id: string
  species: string
  age: number
  age_group: string
  diagnosis: string
  date: Date
  equipment_used: string
  notes: string
  paradigms: Paradigm[]
  recording_type: string
  data_type: string
}

export interface Paradigm {
  _id: string
  paradigm_id: string
  type: string
  start_time: Date
  duration: number
  file: File
  metadata: ParadigmMetadata
}

export interface File {
  _id: string
  file_id: string
  filename: string
  file_size: number
  upload_timestamp: Date
  file_type: string
  file_path: string
  processing_status: string
  processing_metadata: {
    software_version: string
    processing_date: Date
  }
  analyses: Analysis[]
}

export interface Analysis {
  _id: string
  analysis_type: string
  file_path: string
  created_date: Date
  software_used: string
  version: string
}

export interface ParadigmMetadata {
  [key: string]: any
}

export interface Study {
  _id: string
  study_id: string
  study_name: string
  principal_investigator: string
  start_date: Date
  end_date: Date
  description: string
}

function generateParticipant(): Participant {
  const species = faker.helpers.weightedArrayElement([
    { weight: 3, value: "Human" },
    { weight: 1, value: "Mouse" },
  ])
  const age = faker.number.int({ min: 0, max: species === "Human" ? 65 : 2 })
  const ageGroup =
    species === "Human"
      ? age < 3
        ? "infant"
        : age < 18
          ? "pediatric"
          : "adult"
      : age < 0.5
        ? "juvenile"
        : "adult"
  const diagnoses = ["FXS", "Blind", "ASD", "DD", "Control"]
  const diagnosis = faker.helpers.arrayElement(diagnoses)

  const recordingType =
    species === "Human"
      ? "EEG"
      : faker.helpers.weightedArrayElement([
          { weight: 80, value: "MEA" },
          { weight: 10, value: "In Vivo" },
          { weight: 5, value: "Ex Vivo" },
          { weight: 5, value: "In Silico" },
        ])

  return {
    _id: uuidv4(),
    participant_id: faker.string.alphanumeric(6).toUpperCase(),
    demographics: {
      species,
      age,
      age_group: ageGroup,
      gender: faker.person.sex(),
      handedness:
        species === "Human" && ageGroup !== "infant"
          ? faker.helpers.arrayElement(["right", "left", "ambidextrous"])
          : "unknown",
    },
    clinical_measures: {
      diagnosis,
      iq_score:
        species === "Human" && ageGroup !== "infant"
          ? diagnosis !== "Control"
            ? faker.number.int({ min: 40, max: 100 })
            : faker.number.int({ min: 85, max: 115 })
          : null,
      anxiety_level:
        species === "Human" && ageGroup !== "infant"
          ? diagnosis !== "Control"
            ? faker.number.int({ min: 3, max: 10 })
            : faker.number.int({ min: 1, max: 7 })
          : null,
    },
    study_ids: [faker.string.alphanumeric(8).toUpperCase()],
    recording_type: recordingType,
  }
}

function generateSession(participant: Participant): Session {
  const eegid = `D${faker.string.numeric(8)}`
  const paradigms = [
    "rest",
    "chirp",
    "cogflex",
    "revlearn",
    "statlearn",
    "alphabeats",
  ]
  const selectedParadigms = [
    paradigms[0],
    ...faker.helpers.arrayElements(paradigms.slice(1), { min: 1, max: 3 }),
  ]

  return {
    _id: uuidv4(),
    eegid,
    session_id: eegid,
    participant_id: participant.participant_id,
    species: participant.demographics.species,
    age: participant.demographics.age,
    age_group: participant.demographics.age_group,
    diagnosis: participant.clinical_measures.diagnosis,
    date: faker.date.between({
      from: "2013-01-01T00:00:00.000Z",
      to: "2023-05-31T23:59:59.999Z",
    }),
    equipment_used: getEquipmentUsed(
      participant.demographics.age,
      participant.demographics.species,
      participant.recording_type,
    ),
    notes: faker.lorem.sentence(),
    paradigms: selectedParadigms.map((type) => generateParadigm(type, eegid)),
    recording_type: participant.recording_type,
    data_type: faker.helpers.arrayElement(["Resting State", "Task-Related"]),
  }
}

function getEquipmentUsed(
  age: number,
  species: string,
  recordingType: string,
): string {
  if (species === "Human") {
    if (age < 3) {
      return faker.helpers.arrayElement([
        "EGI Hydrocel 128 infant",
        "BioSemi ActiveTwo 32 infant",
      ])
    } else {
      return faker.helpers.arrayElement([
        "EGI Hydrocel 128",
        "BrainVision 64",
        "EGI Hydrocel 32",
      ])
    }
  } else {
    switch (recordingType) {
      case "MEA":
        return faker.helpers.arrayElement([
          "MCS 60-channel MEA",
          "Axion Maestro 768-channel MEA",
        ])
      case "In Vivo":
        return faker.helpers.arrayElement([
          "Neuropixels probe",
          "NeuroNexus silicon probe",
        ])
      case "Ex Vivo":
        return faker.helpers.arrayElement([
          "MultiChannel Systems MEA2100",
          "Alpha MED Scientific MED64",
        ])
      case "In Silico":
        return "NEURON simulation environment"
      default:
        return "Unknown equipment"
    }
  }
}

function generateParadigm(type: string, eegid: string): Paradigm {
  const paradigmId = faker.string.alphanumeric(8).toUpperCase()
  return {
    _id: uuidv4(),
    paradigm_id: paradigmId,
    type,
    start_time: faker.date.recent(),
    duration: faker.number.int({ min: 300, max: 1800 }),
    file: generateFile(eegid, paradigmId, type),
    metadata: generateParadigmMetadata(type),
  }
}

function generateFile(eegid: string, paradigmId: string, type: string): File {
  return {
    _id: uuidv4(),
    file_id: faker.string.alphanumeric(12).toUpperCase(),
    filename: `${eegid}_${paradigmId}_${type}.edf`,
    file_size: faker.number.int({ min: 1000000, max: 100000000 }),
    upload_timestamp: faker.date.recent(),
    file_type: faker.helpers.arrayElement(["EDF", "BDF", "XDF"]),
    file_path: `/data/eeg_files/${eegid}/${paradigmId}.${faker.helpers.arrayElement(["edf", "bdf", "xdf"])}`,
    processing_status: faker.helpers.arrayElement([
      "raw",
      "preprocessed",
      "analyzed",
    ]),
    processing_metadata: {
      software_version: faker.system.semver(),
      processing_date: faker.date.recent(),
    },
    analyses: generateAnalysisFiles(type, eegid, paradigmId),
  }
}

function generateAnalysisFiles(
  type: string,
  eegid: string,
  paradigmId: string,
): Analysis[] {
  const commonAnalyses: Analysis[] = [
    {
      _id: uuidv4(),
      analysis_type: "spectral_power",
      file_path: `/data/analyses/${eegid}/${paradigmId}_spectral_power.csv`,
      created_date: faker.date.recent(),
      software_used: "MNE-Python",
      version: faker.system.semver(),
    },
    {
      _id: uuidv4(),
      analysis_type: "connectivity",
      file_path: `/data/analyses/${eegid}/${paradigmId}_connectivity.mat`,
      created_date: faker.date.recent(),
      software_used: "EEGLAB",
      version: faker.system.semver(),
    },
  ]

  let paradigmSpecificAnalysis: Analysis | null = null
  switch (type) {
    case "resting_state":
      paradigmSpecificAnalysis = {
        _id: uuidv4(),
        analysis_type: "source_localization",
        file_path: `/data/analyses/${eegid}/${paradigmId}_source_localization.nii`,
        created_date: faker.date.recent(),
        software_used: "Brainstorm",
        version: faker.system.semver(),
      }
      break
    case "chirp":
      paradigmSpecificAnalysis = {
        _id: uuidv4(),
        analysis_type: "time_frequency",
        file_path: `/data/analyses/${eegid}/${paradigmId}_time_frequency.mat`,
        created_date: faker.date.recent(),
        software_used: "Fieldtrip",
        version: faker.system.semver(),
      }
      break
    case "cognitive_flexibility":
      paradigmSpecificAnalysis = {
        _id: uuidv4(),
        analysis_type: "erp",
        file_path: `/data/analyses/${eegid}/${paradigmId}_erp.fif`,
        created_date: faker.date.recent(),
        software_used: "MNE-Python",
        version: faker.system.semver(),
      }
      break
  }

  return paradigmSpecificAnalysis
    ? [...commonAnalyses, paradigmSpecificAnalysis]
    : commonAnalyses
}

function generateParadigmMetadata(type: string): ParadigmMetadata {
  switch (type) {
    case "resting_state":
      return {
        eyes: faker.helpers.arrayElement(["open", "closed"]),
        duration: faker.number.int({ min: 300, max: 600 }),
      }
    case "chirp":
      return {
        frequency_range: [
          faker.number.int({ min: 1, max: 10 }),
          faker.number.int({ min: 80, max: 100 }),
        ],
        amplitude: faker.number.float({ min: 0.1, max: 1.0, multipleOf: 0.1 }),
      }
    case "cognitive_flexibility":
      return {
        num_trials: faker.number.int({ min: 50, max: 200 }),
        task_difficulty: faker.helpers.arrayElement(["easy", "medium", "hard"]),
      }
    case "reversal_learning":
      return {
        num_reversals: faker.number.int({ min: 3, max: 10 }),
        stimulus_type: faker.helpers.arrayElement(["visual", "auditory"]),
      }
    case "statistical_learning":
      return {
        sequence_length: faker.number.int({ min: 5, max: 12 }),
        modality: faker.helpers.arrayElement(["visual", "auditory", "tactile"]),
      }
    case "binaural_beats":
      return {
        frequency_left: faker.number.float({
          min: 100,
          max: 500,
          multipleOf: 0.1,
        }),
        frequency_right: faker.number.float({
          min: 100,
          max: 500,
          multipleOf: 0.1,
        }),
        duration: faker.number.int({ min: 300, max: 1200 }),
      }
    default:
      return {}
  }
}

export function generateStudyData(numParticipants: number): {
  study: Study
  participants: Participant[]
  sessions: Session[]
} {
  const study: Study = {
    _id: uuidv4(),
    study_id: faker.string.alphanumeric(8).toUpperCase(),
    study_name: "SignalFlow Vault",
    principal_investigator: faker.person.fullName({ sex: "female" }),
    start_date: faker.date.past({ years: 10 }),
    end_date: faker.date.future({ years: 2 }),
    description:
      "A comprehensive longitudinal study comparing various neurodevelopmental disorders and control groups over the past decade, including both human and mouse models",
  }

  const participants: Participant[] = Array.from(
    { length: numParticipants },
    () => generateParticipant(),
  )

  const sessions: Session[] = participants.flatMap((p) =>
    Array.from({ length: faker.number.int({ min: 1, max: 5 }) }, () =>
      generateSession(p),
    ),
  )

  return { study, participants, sessions }
}

async function createCollections(db: Db) {
  await db.createCollection("sessions")
  await db.createCollection("participants")
  await db.createCollection("studies")
}

async function createIndexes(db: Db) {
  await db
    .collection("sessions")
    .createIndex({ session_id: 1 }, { unique: true })
  await db
    .collection("participants")
    .createIndex({ participant_id: 1 }, { unique: true })
  await db.collection("studies").createIndex({ study_id: 1 }, { unique: true })
}

async function createSampleData(db: Db) {
  const numParticipants = 100 // Adjust this number as needed
  const { study, participants, sessions } = generateStudyData(numParticipants)

  await db.collection("studies").insertOne(study)
  await db.collection("participants").insertMany(participants)

  // Insert sessions in batches to avoid potential duplicate key errors
  const batchSize = 50
  for (let i = 0; i < sessions.length; i += batchSize) {
    const batch = sessions.slice(i, i + batchSize)
    try {
      await db.collection("sessions").insertMany(batch, { ordered: false })
    } catch (error) {
      console.error("Error inserting sessions batch:", error)
      // Continue with the next batch even if there's an error
    }
  }
}

export async function initializeDatabase() {
  const db = await getDb()
  await createCollections(db)
  await createIndexes(db)
  await createSampleData(db)
  return {
    message: "Database initialized successfully with realistic sample data",
  }
}
