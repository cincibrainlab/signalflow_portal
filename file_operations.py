import os
import json
import hashlib
import logging
from db import get_db_session
from models import EEGFileCatalog, DatasetCatalog, UploadCatalog
import shutil
import datetime

logging.basicConfig(
    filename='portal_files/logs/eeg_file_catalog.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def add_uppy_metadata_to_db(info_files):
    session = get_db_session()

    def extract_metadata(info_file, folder_path='./portal_files/uploads/'):
        with open(info_file, 'r') as f:
            file_metadata = json.load(f)
        row = {
            'status': add_status_code(200),
            'dataset_name': file_metadata['MetaData'].get('datasetName', 'NA'),
            'remove_upload': False,
            'upload_id': file_metadata.get('ID', 'NA'),
            'date_added': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'size': file_metadata.get('Size', 'NA'),
            'original_name': file_metadata['MetaData'].get('filename', 'NA'),
            'hash': create_file_hash(os.path.join(folder_path, os.path.basename(file_metadata['Storage'].get('Path', ''))))
        }
        return row

    for info_file in info_files:
        row = extract_metadata(info_file)
        dataset_name = row['dataset_name']
        dataset = session.query(DatasetCatalog).filter_by(dataset_name=dataset_name).first()
        if not dataset:
            dataset = DatasetCatalog(dataset_name=dataset_name)
            session.add(dataset)
            session.commit()
        eeg_file = UploadCatalog(dataset_id=dataset.id, **row)
        session.merge(eeg_file)
        session.commit()
        logging.info(f"Metadata added to database for file: {row['original_name']}")
    session.close()

def align_fdt_files(folder_path='./portal_files/uploads/'):
    session = get_db_session()
    for row in session.query(EEGFileCatalog).all():
        if row.filename.endswith('.set'):
            fdt_filename = row.filename.replace('.set', '.fdt')
            fdt_file = session.query(EEGFileCatalog).filter(EEGFileCatalog.filename == fdt_filename).first()
            if fdt_file:
                row.has_fdt_file = True
                row.fdt_filename = os.path.join(folder_path, fdt_filename)
            else:
                row.has_fdt_file = False
                row.fdt_filename = os.path.join(folder_path, fdt_filename)
        session.merge(row)
    session.commit()

def scan_new_files():
    session = get_db_session()
    for row in session.query(EEGFileCatalog).filter(EEGFileCatalog.status == 'NEW').all():
        logging.info("Scanning new files - Filename: %s, Status: %s", row.filename, row.status)

def move_new_files_to_import_folder():
    session = get_db_session()
    for row in session.query(EEGFileCatalog).filter(EEGFileCatalog.status == 'NEW').all():
        logging.info("Processing file for import: %s with status: %s", row.filename, row.status)
        try:
            import_single_file(row.upload_id, row.filename)
            row.status = add_status_code(201)
            row.remove_upload = True
            session.merge(row)
            session.commit()
            logging.info("Successfully imported file: %s", row.filename)
        except Exception as e:
            logging.exception("Failed to import file: %s. Exception: %s", row.filename, e)
            row.status = add_status_code(500)
            row.remove_upload = False
            session.merge(row)
            session.commit()
            continue

def import_single_file( uppy_id, orginal_file_name, root_folder='./portal_files/'):
    # Move the file to the import folder
    import_folder = os.path.join(root_folder, 'import')  # Replace with the actual import folder path
    upload_folder = os.path.join(root_folder, 'uploads')  # Replace with the actual upload folder path

    uppy_storage_path = os.path.join(upload_folder, uppy_id)
    imported_storage_path = os.path.join(import_folder, orginal_file_name)

    if not os.path.exists(imported_storage_path):
        shutil.copy(uppy_storage_path, imported_storage_path)
    else:
        print(f"File already exists at {imported_storage_path}. Skipping move operation.")

def delete_uploaded_files_and_move_info():
    session = get_db_session()
    upload_folder = './portal_files/uploads/'  # Replace with the actual upload folder path
    info_archive_folder = './portal_files/info_archive/'  # Replace with the actual info archive folder path
    for row in session.query(EEGFileCatalog).filter(EEGFileCatalog.remove_upload).all():
        upload_path = os.path.join(upload_folder, row.upload_id)
        info_file_path = os.path.join(upload_folder, f"{row.upload_id}.info")  # Assuming the info file follows this naming convention
        archive_info_path = os.path.join(info_archive_folder, f"{row.upload_id}.info")
        if os.path.exists(upload_path):
            try:
                os.remove(upload_path)
                logging.info("Successfully deleted uploaded file: %s", row.upload_id)
                if os.path.exists(info_file_path):
                    shutil.move(info_file_path, archive_info_path)
                    logging.info("Successfully moved info file to archive: %s", f"{row.upload_id}.info")
            except Exception as e:
                logging.exception("Failed to process uploaded file: %s. Exception: %s", row.upload_id, e)

def add_eeg_metadata_to_db():
    session = get_db_session()
    for row in session.query(EEGFileCatalog).all():
        if row.filename.endswith('.set'):
            print(row.filename)

def add_metadata_to_db(info_files):
    add_uppy_metadata_to_db(info_files)
    #align_fdt_files()
    #add_eeg_metadata_to_db()

def create_file_hash(file_path):
    hash_blake2 = hashlib.blake2b()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_blake2.update(chunk)
    return hash_blake2.hexdigest()

def add_status_code(code):
    if code == 200:
        return 'NEW'
    elif code == 201:
        return 'IMPORTED'
    elif code == 204:
        return 'DELETED'
    else:
        return 'ERROR'

if __name__ == "__main__":
    scan_new_files()
    move_new_files_to_import_folder()
    delete_uploaded_files_and_move_info()