import hashlib
import yaml

def load_config(file_path="portal_config.yaml"):
    try:
        with open(file_path, 'r') as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except yaml.YAMLError as exc:
        print(exc)

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