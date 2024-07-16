import os
import imghdr
import re
from pathlib import Path
from json_helper import *

def get_filename(file_path):
    return Path(file_path).name

def rename_heic_to_jpeg(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.heic'):
                file_path = Path(root) / file
                try:
                    # Check if the file is actually a JPEG
                    if imghdr.what(file_path) == 'jpeg':
                        # Construct the new file name with .jpg extension
                        new_file_path = file_path.with_suffix('.jpg')
                        json_path = get_json_path(file_path)
                        new_json_path = replace_heic_with_jpg(json_path)
                        # Rename the file
                        file_path.rename(new_file_path)
                        json_path.rename(new_json_path)
                        print(f"Renamed: {file_path} to {get_filename(new_file_path)}")
                        print(f"and {get_filename(json_path)} to {get_filename(new_json_path)}\n")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

def replace_heic_with_jpg(file_path):
    # Convert to Path object if it's a string
    path = Path(file_path) if isinstance(file_path, str) else file_path
    
    # Get the name and parent directory
    name = path.name
    parent = path.parent
    
    # Replace HEIC with jpg in the filename
    new_name = name.replace('HEIC', 'jpg').replace('heic', 'jpg')
    
    # Return a new Path object with the modified name
    return parent / new_name

# Usage
takeout_path = "/Volumes/Ady_2tb_red/takeout_extract3/Takeout/Google Photos"
rename_heic_to_jpeg(takeout_path)