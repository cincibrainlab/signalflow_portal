from pydantic import BaseModel
from datetime import datetime

# Define the collections
class Participant(BaseModel):
    participant_id: str
    species: str
    age: int
    age_group: str
    gender: str
    handedness: str
    diagnosis: str
    iq_score: int
    anxiety_level: int
    
class Study(BaseModel):
    study_name: str
    principal_investigator: str
    start_date: datetime
    end_date: datetime
    description: str

class File(BaseModel):
    status: str
    upload_id: str
    date_added: str
    original_name: str
    eeg_format: str
    eeg_paradigm: str
    is_set_file: bool
    has_fdt_file: bool
    fdt_filename: str
    fdt_upload_id: str
    upload_email: str
    hash: str
    metadata: str

class Paradigms(BaseModel):
    ParadigmName: str
    Study: Study
    
class ParadigmTrial(BaseModel):
    paradigm: Paradigms
    start_time: datetime
    duration: int
    file: File

class Session(BaseModel):
    participant_id: Participant
    paradigm_trials: list[ParadigmTrial]
    date: str
    equipment_used: str
    notes: str
    recording_type: str
    data_type: str
    
class FileStatus(BaseModel):
    file_id: File
    current_status: str
    
class EegAnalysis(BaseModel):
    name: str
    function_name: str
    description: str
    category: str
    valid_formats: str
    valid_paradigms: list[Paradigms]
    valid_files: list[File]
    files: list[FileStatus]
    parameters: str
    
    








# EegAnalysis {
# 	name: string
# 	function_name string
# 	description: string
# 	category: string
# 	valid_formats: string
# 	valid_paradigms: string *>* Paradigms.id
# 	valid_FIles integer *>* File.id
# 	files integer *>* FileStatus.id
# 	parameters: string
# }


# FileStatus {
# 	id integer pk increments unique
# 	file_id integer > File.id
# 	current_status string
# }

# # Define the collections 
# class EEGFormat(BaseModel):
#     id: str
#     name: str
#     description: str

# class EEGParadigm(BaseModel):
#     id: str
#     name: str
#     description: str

# class Email(BaseModel):
#     id: str
#     name: str

# # Files Tab
# class UploadCatalog(BaseModel):
#     upload_id: str | None = None
#     original_name: str | None = None
#     is_set_file: bool | None = None
#     has_fdt_file: bool | None = None
#     fdt_filename: str | None = None
#     fdt_upload_id: str | None = None
#     dataset_id: str | None = None
#     dataset_name: str | None = None
#     eeg_format: str | None = None
#     eeg_paradigm: str | None = None
#     upload_email: str | None = None
#     status: str | None = None
#     date_added: str | None = None
#     hash: str | None = None
#     size: int | None = None
#     remove_upload: bool | None = None

# class ImportCatalog(BaseModel):
#     upload_id: str | None
#     original_name: str | None
#     is_set_file: bool | None
#     has_fdt_file: bool | None
#     fdt_filename: str | None
#     fdt_upload_id: str | None
#     dataset_id: str | None
#     dataset_name: str | None
#     eeg_format: str | None
#     eeg_paradigm: str | None
#     upload_email: str | None
#     status: str | None
#     date_added: str | None
#     hash: str | None
#     remove_import: bool | None
#     sample_rate: int | None
#     n_channels: int | None
#     n_epochs: int | None
#     total_samples: int | None
#     mne_load_error: bool | None

# class DatasetCatalog(BaseModel):
#     dataset_name: str | None
#     dataset_id: str | None
#     description: str | None

