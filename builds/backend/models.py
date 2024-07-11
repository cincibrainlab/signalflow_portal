from pydantic import BaseModel
from datetime import datetime

# Define the collections
class Participant(BaseModel):
    participant_id: str | None
    species: str | None
    age: int | None
    age_group: str | None
    gender: str | None
    handedness: str | None
    diagnosis: str | None
    iq_score: int | None
    anxiety_level: int | None
    
class Study(BaseModel):
    study_name: str | None
    principal_investigator: str | None
    start_date: datetime | None
    end_date: datetime | None
    description: str | None
    
class EEGFormat(BaseModel):
    name: str | None
    description: str | None
    
class EEGParadigm(BaseModel):
    name: str | None
    description: str | None
    Study: Study | None
    
class User(BaseModel):
    username: str | None
    email: str | None
    password: str | None
    is_active: bool | None
    is_superuser: bool | None

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
    paradigm_start_time: datetime | None
    paradigm_duration: int | None
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
    participant: Participant | None
    
class File(BaseModel):
    status: str | None
    upload_id: str | None
    date_added: str | None
    original_file: OriginalImportFile | None
    eeg_format: EEGFormat | None
    is_set_file: bool | None
    has_fdt_file: bool | None
    fdt_filename: str | None
    fdt_upload_id: str | None
    hash: str | None
    metadata: str | None
    status: str | None
    
class Dataset(BaseModel):
    dataset_name: str | None
    dataset_id:str | None
    description: str | None
    files: list[File] | None
    status: str | None
    date_added: str | None
    date_modified: str | None

class Session(BaseModel):
    participant_id: Participant | None
    paradigm_trials: list[File] | None
    date: str | None
    equipment_used: str | None
    notes: str | None
    recording_type: str | None
    data_type: str | None
    
class FileStatus(BaseModel):
    file_id: File | None
    current_status: str | None
    
class EegAnalysis(BaseModel):
    name: str | None
    function_name: str | None
    description: str | None
    category: str | None
    valid_formats: list[str] | None
    valid_paradigms: list[EEGParadigm] | None
    valid_files: list[File] | None
    files: list[FileStatus] | None
    parameters: str | None
    
class UserGroup(BaseModel):
    name: str | None
    description: str | None
    users: list[User] | None
    paradigms: list[EEGParadigm] | None
    studies: list[Study] | None
    datasets: list[Dataset] | None
    participants: list[Participant] | None
    files: list[File] | None
    originalFiles: list[OriginalImportFile] | None
    eegAnalyses: list[EegAnalysis] | None
    sessions: list[Session] | None
    
    

