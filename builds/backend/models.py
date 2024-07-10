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
    
class EEGFormat(BaseModel):
    name: str
    description: str
    
class EEGParadigm(BaseModel):
    name: str
    description: str
    Study: Study
    
class User(BaseModel):
    username: str
    email: str
    password: str
    is_active: bool
    is_superuser: bool

class OriginalImportFile(BaseModel):
    upload_id: str | None
    original_name: str | None
    is_set_file: bool | None
    has_fdt_file: bool | None
    fdt_filename: str | None
    fdt_upload_id: str | None
    dataset_id: str | None
    eeg_format: EEGFormat | None
    eeg_paradigm: EEGParadigm | None
    paradigm_start_time: datetime
    paradigm_duration: int
    upload_user: User | None
    status: str | None
    date_added: str | None
    hash: str | None
    remove_upload: bool | None
    sample_rate: int | None
    n_channels: int | None
    n_epochs: int | None
    total_samples: int | None
    mne_load_error: bool | None
    
class File(BaseModel):
    status: str
    upload_id: str
    date_added: str
    original_file: OriginalImportFile
    eeg_format: EEGFormat
    is_set_file: bool
    has_fdt_file: bool
    fdt_filename: str
    fdt_upload_id: str
    hash: str
    metadata: str
    status: str
    
class Dataset(BaseModel):
    dataset_name: str
    dataset_id:str
    description: str
    files: list[File]
    status: str
    date_added: str
    date_modified: str

class Session(BaseModel):
    participant_id: Participant
    paradigm_trials: list[File]
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
    valid_paradigms: list[EEGParadigm]
    valid_files: list[File]
    files: list[FileStatus]
    parameters: str
    
class UserGroup(BaseModel):
    name: str
    description: str
    users: list[User]
    paradigms: list[EEGParadigm]
    studies: list[Study]
    datasets: list[Dataset]
    participants: list[Participant]
    files: list[File]
    originalFiles: list[OriginalImportFile]
    eegAnalyses: list[EegAnalysis]
    sessions: list[Session]
    
    

