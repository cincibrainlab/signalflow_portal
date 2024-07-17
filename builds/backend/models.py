from pydantic import BaseModel, Field
from typing import Optional, Any
from bson import ObjectId
from pydantic_core import core_schema
from datetime import datetime

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")

        return ObjectId(value)

# Define the collections
    
class Participant(BaseModel):
    participant_id: Optional[str] = Field(default="")
    species: Optional[str] = Field(default="")
    age: Optional[int] = Field(default=-1)
    age_group: Optional[str] = Field(default="")
    gender: Optional[str] = Field(default="")
    handedness: Optional[str] = Field(default="")
    diagnosis: Optional[str] = Field(default="")
    iq_score: Optional[int] = Field(default=-1)
    anxiety_level: Optional[int] = Field(default=-1)
    
class Study(BaseModel):
    study_name: Optional[str] = Field(default="")
    principal_investigator: Optional[str] = Field(default="")
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    description: Optional[str] = Field(default="")
    
class EEGFormat(BaseModel):
    name: Optional[str] = Field(default="")
    description: Optional[str] = Field(default="")
    
class FormInfo(BaseModel):
    name: Optional[str] = Field(default="")
    description: Optional[str] = Field(default="")
    form_options: Optional[list[str]] = Field(default=None)
    
class EEGParadigm(BaseModel):
    name: Optional[str] = Field(default="")
    description: Optional[str] = Field(default="")
    study: Optional[PyObjectId] = Field(default=None)
    
class User(BaseModel):
    username: Optional[str] = Field(default="")
    email: Optional[str] = Field(default="")
    password: Optional[str] = Field(default="")
    is_active: Optional[bool] = Field(default=None)
    is_superuser: Optional[bool] = Field(default=None)

class OriginalImportFile(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    upload_id: Optional[str] = Field(default="")
    original_name: Optional[str] = Field(default="")
    is_set_file: Optional[bool] = Field(default=None)
    has_fdt_file: Optional[bool] = Field(default=None)
    fdt_filename: Optional[str] = Field(default="")
    fdt_upload_id: Optional[str] = Field(default="")
    dataset_id: Optional[str] = Field(default="")
    eeg_format: Optional[PyObjectId] = Field(default=None)
    eeg_paradigm: Optional[PyObjectId] = Field(default=None)
    paradigm_start_time: Optional[datetime] = Field(default=None)
    paradigm_duration: Optional[int] = Field(default=-1)
    upload_user: Optional[User] = Field(default=None)
    status: Optional[str] = Field(default="")
    date_added: Optional[str] = Field(default="")
    hash: Optional[str] = Field(default="")
    remove_upload: Optional[bool] = Field(default=None)
    sample_rate: Optional[int] = Field(default=-1)
    n_channels: Optional[int] = Field(default=-1)
    n_epochs: Optional[int] = Field(default=-1)
    total_samples: Optional[int] = Field(default=-1)
    mne_load_error: Optional[bool] = Field(default=None)
    participant: Optional[PyObjectId] = Field(default=None)
    eegid: Optional[str] = Field(default="")
    
class File(BaseModel):
    upload_id: Optional[str] = Field(default="")
    date_added: Optional[str] = Field(default="")
    original_file: Optional[PyObjectId] = Field(default=None)
    eeg_format: Optional[PyObjectId] = Field(default=None)
    is_set_file: Optional[bool] = Field(default=None)
    has_fdt_file: Optional[bool] = Field(default=None)
    fdt_filename: Optional[str] = Field(default="")
    fdt_upload_id: Optional[str] = Field(default="")
    hash: Optional[str] = Field(default="")
    metadata: Optional[str] = Field(default="")
    status: Optional[str] = Field(default="")
    current_status: Optional[str] = Field(default="")
    
class Dataset(BaseModel):
    dataset_name: Optional[str] = Field(default="")
    dataset_id: Optional[str] = Field(default="")
    description: Optional[str] = Field(default="")
    files: Optional[list[PyObjectId]] = Field(default=None)
    status: Optional[str] = Field(default="")
    date_added: Optional[str] = Field(default="")
    date_modified: Optional[str] = Field(default="")

class Session(BaseModel):
    participant: Optional[PyObjectId] = Field(default=None)
    paradigm_trials: Optional[list[PyObjectId]] = Field(default=None)
    date: Optional[str] = Field(default="")
    equipment_used: Optional[str] = Field(default="")
    notes: Optional[str] = Field(default="")
    recording_type: Optional[str] = Field(default="")
    data_type: Optional[str] = Field(default="")
    
    
class EegAnalysis(BaseModel):
    name: Optional[str] = Field(default="")
    function_name: Optional[str] = Field(default="")
    description: Optional[str] = Field(default="")
    category: Optional[str] = Field(default="")
    valid_formats: Optional[list[str]] = Field(default=None) #TODO Consider linking to obj ID
    valid_paradigms: Optional[list[str]] = Field(default=None) #TODO Consider linking to obj ID
    valid_files: Optional[list[str]] = Field(default=None) #List of mongo Obj ID's for compatible originalImportFiles
    files: Optional[list[str]] = Field(default=None) #List of obj Id's for 
    parameters: Optional[str] = Field(default="")
    
class UserGroup(BaseModel):
    name: Optional[str] = Field(default="")
    description: Optional[str] = Field(default="")
    users: Optional[list[PyObjectId]] = Field(default=None)
    paradigms: Optional[list[PyObjectId]] = Field(default=None)
    studies: Optional[list[PyObjectId]] = Field(default=None)
    datasets: Optional[list[PyObjectId]] = Field(default=None)
    participants: Optional[list[PyObjectId]] = Field(default=None)
    files: Optional[list[PyObjectId]] = Field(default=None)
    originalFiles: Optional[list[PyObjectId]] = Field(default=None)
    eegAnalyses: Optional[list[PyObjectId]] = Field(default=None)
    sessions: Optional[list[PyObjectId]] = Field(default=None)
    
    

