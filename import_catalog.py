
from shutil import copy
import os
from db import get_db_session
from models import UploadCatalog, ImportCatalog
from portal_utils import add_status_code, load_config
from upload_catalog import get_upload_and_fdt_upload_id
from signal_utils import get_core_eeg_info

config = load_config()
UPLOAD_PATH = config['folder_paths']['uploads']
IMPORT_PATH = config['folder_paths']['import']
INFO_PATH = config['folder_paths']['info_archive']

def update_import_catalog():
    session = get_db_session()
    set_files = session.query(UploadCatalog).filter(UploadCatalog.is_set_file).all()
    for file in set_files:
        set_dest_path, fdt_dest_path = copy_import_files(file.upload_id)
        core_info = get_core_eeg_info(set_dest_path)
        import_record = ImportCatalog(
            original_name=file.original_name,
            dataset_name=file.dataset_name,
            dataset_id=file.dataset_id,
            date_added=file.date_added,
            upload_id=file.upload_id,  # Assuming the import_id can be the same as upload_id for simplicity
            remove_import=file.remove_upload,
            is_set_file=file.is_set_file,
            has_fdt_file=file.has_fdt_file,
            fdt_filename=file.fdt_filename,
            fdt_upload_id=file.fdt_upload_id,
            hash=file.hash,
            mne_load_error=core_info['mne_load_error'],
            sample_rate = core_info['sample_rate'],
            n_channels = core_info['n_channels'],
            n_epochs = core_info['n_epochs'],
            total_samples = core_info['total_samples']
        )
        if import_record.mne_load_error:
            import_record.status=add_status_code(500)
        else:
            import_record.status=add_status_code(201)
        session.add(import_record)
        clean_import_files(file.upload_id)
    session.commit()
    print(f"Transferred {len(set_files)} SET files from UploadCatalog to ImportCatalog.")

def copy_import_files(upload_id):
    # Copy the SET and FDT files to the import path
    import_file_paths = get_upload_and_fdt_upload_id(upload_id)
    set_dest_path = import_file_paths['set_import_path']
    fdt_dest_path = import_file_paths['fdt_import_path']
    set_src_path = import_file_paths['set_upload_path']
    fdt_src_path = import_file_paths['fdt_upload_path']

    if set_src_path:
        copy(set_src_path, set_dest_path)
        print(f"Copied SET file {set_src_path} to {set_dest_path}")
    
    if fdt_src_path:
        copy(fdt_src_path, fdt_dest_path)
        print(f"Copied FDT file {fdt_src_path} to {fdt_dest_path}")
    return set_dest_path, fdt_dest_path

def clean_import_files(upload_id):
    import_file_paths = get_upload_and_fdt_upload_id(upload_id)
    set_dest_path = import_file_paths['set_import_path']
    fdt_dest_path = import_file_paths['fdt_import_path']

    if os.path.exists(set_dest_path):
        os.remove(set_dest_path)
        print(f"Removed SET file {set_dest_path}")
    if fdt_dest_path and os.path.exists(fdt_dest_path):
        os.remove(fdt_dest_path)
        print(f"Removed FDT file {fdt_dest_path}")
    
def update_core_eeg_info():
    session = get_db_session()
    for record in session.query(ImportCatalog).all():
        if record.is_set_file:
            set_dest_path, fdt_dest_path = copy_import_files(record.upload_id)
            core_eeg_info = get_core_eeg_info(set_dest_path)
            record.core_eeg_info = core_eeg_info
        session.merge(record)
    session.commit()

def get_first_upload_id():
    session = get_db_session()
    first_import_record = session.query(ImportCatalog).first()
    if first_import_record:
        return first_import_record.upload_id
    else:
        return None

def get_upload_id_by_record_number(record_number=None):
    session = get_db_session()
    if record_number is not None:
        try:
            record = session.query(ImportCatalog).offset(record_number - 1).first()
            if record:
                return record.upload_id
            else:
                print(f"No record found for record number: {record_number}")
                return None
        except Exception as e:
            print(f"Error retrieving upload_id for record number {record_number}: {e}")
            return None
    else:
        try:
            records = session.query(ImportCatalog).all()
            if records:
                print("Available records:")
                for record in records:
                    print(f"Record Number: {records.index(record) + 1}, Upload ID: {record.upload_id}")
            else:
                print("No records found.")
        except Exception as e:
            print(f"Error retrieving records: {e}")
