import os
import json
from datetime import datetime
import hashlib

def get_photo_year(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    timestamp = int(data['photoTakenTime']['timestamp'])
    return datetime.fromtimestamp(timestamp).year

def get_file_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def is_supported_image(filename):
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.heic')
    return filename.lower().endswith(supported_extensions)

def scan_albums(takeout_path):
    for root, dirs, files in os.walk(takeout_path):
        if not os.path.basename(root).startswith('Photos from '):  # Check if it's an album folder
            for file in files:
                if is_supported_image(file):
                    album_file_path = os.path.join(root, file)
                    json_file = album_file_path + '.json'
                    
                    if not os.path.exists(json_file):
                        print(f"Warning: JSON file not found for {album_file_path}")
                        continue
                    
                    photo_year = get_photo_year(json_file)
                    library_year_folder = f"Photos from {photo_year}"
                    library_file_path = os.path.join(takeout_path, library_year_folder, file)

                    if not os.path.exists(library_file_path):
                        print(f"File not found in library: {album_file_path}")
                    else:
                        album_file_hash = get_file_hash(album_file_path)
                        library_file_hash = get_file_hash(library_file_path)
                        
                        if album_file_hash != library_file_hash:
                            print(f"File content mismatch: {album_file_path}")

if __name__ == "__main__":
    #takeout_path = "/Users/martonady/Downloads/test_ori"
    takeout_path = "/Volumes/Ady_2tb_red/takeout_extract2/Takeout/Google Photos"
    scan_albums(takeout_path)