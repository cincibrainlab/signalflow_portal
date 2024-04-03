from db import get_db_session
from models import DatasetCatalog, UploadCatalog, ImportCatalog
from  portal_utils import create_file_hash, add_status_code, load_config

config = load_config()
UPLOAD_PATH = config['folder_paths']['uploads']
IMPORT_PATH = config['folder_paths']['import']

def update_import_catalog():
    session = get_db_session()
    set_files = session.query(UploadCatalog).filter(UploadCatalog.is_set_file == True).all()
    for file in set_files:
        import_record = ImportCatalog(
            original_name=file.original_name,
            dataset_name=file.dataset_name,
            dataset_id=file.dataset_id,
            status=file.status,
            date_added=file.date_added,
            upload_id=file.upload_id,  # Assuming the import_id can be the same as upload_id for simplicity
            remove_import=file.remove_upload,
            is_set_file=file.is_set_file,
            has_fdt_file=file.has_fdt_file,
            fdt_filename=file.fdt_filename
        )
        session.add(import_record)
        session.delete(file)  # Remove the record from UploadCatalog after transferring
    session.commit()
    print(f"Transferred {len(set_files)} SET files from UploadCatalog to ImportCatalog.")

