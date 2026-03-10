import uuid
import os

def generate_uuid():
    return str(uuid.uuid4())

def delete_file_from_disk(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Error deleting file {path}: {e}")