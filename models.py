from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class EEGFileCatalog(Base):
    __tablename__ = 'eeg_file_catalog'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    dataset_name = Column(String)
    storage = Column(Text, unique=True)
    upload_id = Column(String, unique=True)
    size = Column(String)
    dataset_id = Column(Integer)
    hash = Column(String)
    has_fdt_file = Column(Boolean)
    fdt_filename = Column(String)
    set_filename = Column(String)
    status = Column(String)
    remove_upload = Column(Boolean)

class CatalogBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    status = Column(String)
    upload_id = Column(String, unique=True)
    date_added = Column(String)
    original_name = Column(String)
    dataset_name = Column(String)
    dataset_id = Column(Integer)
    is_set_file = Column(Boolean)
    has_fdt_file = Column(Boolean)
    fdt_filename = Column(String)
    fdt_upload_id = Column(String)
    hash = Column(String)

class UploadCatalog(CatalogBase):
    __tablename__ = 'upload_catalog'
    size = Column(String)
    remove_upload = Column(Boolean)
    
class ImportCatalog(CatalogBase):
    __tablename__ = 'import_catalog'
    remove_import = Column(Boolean, name='remove')
    sample_rate = Column(Integer)
    n_channels = Column(Integer)
    n_epochs = Column(Integer)
    total_samples = Column(Integer)
    mne_load_error = Column(Boolean)

class AnalysisCatalog(CatalogBase):
    __tablename__ = 'analysis_catalog'
    analysis_id = Column(String, unique=True)
    remove_analysis = Column(Boolean, name='remove')

class DatasetCatalog(Base):
    __tablename__ = 'dataset_catalog'
    id = Column(Integer, primary_key=True)
    dataset_name = Column(String, unique=True)
    description = Column(Text)
    eeg_format = Column(Integer)
    is_event_related = Column(Integer)