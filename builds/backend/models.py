from pydantic import BaseModel
from datetime import datetime

# Define the collections
class Participant(BaseModel):
    participant_id: str | None = None
    species: str | None = None
    age: int | None = None
    age_group: str | None = None
    gender: str | None = None
    handedness: str | None = None
    diagnosis: str | None = None
    iq_score: int | None = None
    anxiety_level: int | None = None
    
class Study(BaseModel):
    study_name: str | None = None
    principal_investigator: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    description: str | None = None
    
class EEGFormat(BaseModel):
    name: str | None = None
    description: str | None = None
    
class EEGParadigm(BaseModel):
    name: str | None = None
    description: str | None = None
    study: Study | None = None
    
class User(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None

class OriginalImportFile(BaseModel):
    upload_id: str | None = None
    original_name: str | None = None
    is_set_file: bool | None = None
    has_fdt_file: bool | None = None
    fdt_filename: str | None = None
    fdt_upload_id: str | None = None
    dataset_id: str | None = None
    eeg_format: EEGFormat | None = None
    eeg_paradigm: EEGParadigm | None = None
    paradigm_start_time: datetime | None = None
    paradigm_duration: int | None = None
    upload_user: User | None = None
    status: str | None = None
    date_added: str | None = None
    hash: str | None = None
    remove_upload: bool | None = None
    sample_rate: int | None = None
    n_channels: int | None = None
    n_epochs: int | None = None
    total_samples: int | None = None
    mne_load_error: bool | None = None
    participant: Participant | None = None
    
class File(BaseModel):
    status: str | None = None
    upload_id: str | None = None
    date_added: str | None = None
    original_file: OriginalImportFile | None = None
    eeg_format: EEGFormat | None = None
    is_set_file: bool | None = None
    has_fdt_file: bool | None = None
    fdt_filename: str | None = None
    fdt_upload_id: str | None = None
    hash: str | None = None
    metadata: str | None = None
    status: str | None = None
    
class Dataset(BaseModel):
    dataset_name: str | None = None
    dataset_id:str | None = None
    description: str | None = None
    files: list[File] | None = None
    status: str | None = None
    date_added: str | None = None
    date_modified: str | None = None

class Session(BaseModel):
    participant_id: Participant | None = None
    paradigm_trials: list[File] | None = None
    date: str | None = None
    equipment_used: str | None = None
    notes: str | None = None
    recording_type: str | None = None
    data_type: str | None = None
    
class FileStatus(BaseModel):
    file_id: File | None = None
    current_status: str | None = None
    
class EegAnalysis(BaseModel):
    name: str | None = None
    function_name: str | None = None
    description: str | None = None
    category: str | None = None
    valid_formats: list[str] | None = None
    valid_paradigms: list[EEGParadigm] | None = None
    valid_files: list[File] | None = None
    files: list[FileStatus] | None = None
    parameters: str | None = None
    
class UserGroup(BaseModel):
    name: str | None = None
    description: str | None = None
    users: list[User] | None = None
    paradigms: list[EEGParadigm] | None = None
    studies: list[Study] | None = None
    datasets: list[Dataset] | None = None
    participants: list[Participant] | None = None
    files: list[File] | None = None
    originalFiles: list[OriginalImportFile] | None = None
    eegAnalyses: list[EegAnalysis] | None = None
    sessions: list[Session] | None = None
    
    

