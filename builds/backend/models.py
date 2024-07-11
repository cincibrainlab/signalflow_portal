from pydantic import BaseModel
from datetime import datetime

# Define the collections
class Participant(BaseModel):
    participant_id: str | None = ''
    species: str | None = ''
    age: int | None = -1
    age_group: str | None = ''
    gender: str | None = ''
    handedness: str | None = ''
    diagnosis: str | None = ''
    iq_score: int | None = -1
    anxiety_level: int | None = -1
    
class Study(BaseModel):
    study_name: str | None = ''
    principal_investigator: str | None = ''
    start_date: datetime | None = None
    end_date: datetime | None = None
    description: str | None = ''
    
class EEGFormat(BaseModel):
    name: str | None = ''
    description: str | None = ''
    
class EEGParadigm(BaseModel):
    name: str | None = ''
    description: str | None = ''
    study: Study | None = None
    
class User(BaseModel):
    username: str | None = ''
    email: str | None = ''
    password: str | None = ''
    is_active: bool | None = None
    is_superuser: bool | None = None

class OriginalImportFile(BaseModel):
    upload_id: str | None = ''
    original_name: str | None = ''
    is_set_file: bool | None = None
    has_fdt_file: bool | None = None
    fdt_filename: str | None = ''
    fdt_upload_id: str | None = ''
    dataset_id: str | None = ''
    eeg_format: EEGFormat | None = EEGFormat()
    eeg_paradigm: EEGParadigm | None = EEGParadigm()
    paradigm_start_time: datetime | None = None
    paradigm_duration: int | None = -1
    upload_user: User | None = User()
    status: str | None = ''
    date_added: str | None = ''
    hash: str | None = ''
    remove_upload: bool | None = None
    sample_rate: int | None = -1
    n_channels: int | None = -1
    n_epochs: int | None = -1
    total_samples: int | None = -1
    mne_load_error: bool | None = None
    participant: Participant | None = Participant()
    eegid: str | None = ''
    
class File(BaseModel):
    status: str | None = ''
    upload_id: str | None = ''
    date_added: str | None = ''
    original_file: OriginalImportFile | None = None
    eeg_format: EEGFormat | None = None
    is_set_file: bool | None = None
    has_fdt_file: bool | None = None
    fdt_filename: str | None = ''
    fdt_upload_id: str | None = ''
    hash: str | None = ''
    metadata: str | None = ''
    status: str | None = ''
    
class Dataset(BaseModel):
    dataset_name: str | None = ''
    dataset_id:str | None = ''
    description: str | None = ''
    files: list[File] | None = None
    status: str | None = ''
    date_added: str | None = ''
    date_modified: str | None = ''

class Session(BaseModel):
    participant_id: Participant | None = Participant()
    paradigm_trials: list[File] | None = None
    date: str | None = ''
    equipment_used: str | None = ''
    notes: str | None = ''
    recording_type: str | None = ''
    data_type: str | None = ''
    
class FileStatus(BaseModel):
    file_id: File | None = None
    current_status: str | None = ''
    
class EegAnalysis(BaseModel):
    name: str | None = ''
    function_name: str | None = ''
    description: str | None = ''
    category: str | None = ''
    valid_formats: list[str] | None = None
    valid_paradigms: list[EEGParadigm] | None = None
    valid_files: list[File] | None = None
    files: list[FileStatus] | None = None
    parameters: str | None = ''
    
class UserGroup(BaseModel):
    name: str | None = ''
    description: str | None = ''
    users: list[User] | None = None
    paradigms: list[EEGParadigm] | None = None
    studies: list[Study] | None = None
    datasets: list[Dataset] | None = None
    participants: list[Participant] | None = None
    files: list[File] | None = None
    originalFiles: list[OriginalImportFile] | None = None
    eegAnalyses: list[EegAnalysis] | None = None
    sessions: list[Session] | None = None
    
    

