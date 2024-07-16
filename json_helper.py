import os
import re
from pathlib import Path
import json
from datetime import datetime, timezone

from pathlib import Path
import re

from PIL import Image
import piexif

from jpeg_helper import *
from heic_helper import *

def get_json_path(file_path):
    # Convert to Path object if it's a string
    file_path = Path(file_path)
    # Remove the extension
    base_name = file_path.stem
    original_extension = file_path.suffix.lower()
    
    # Generate potential file paths based on the rules
    potential_paths = []
    
    # Default case
    potential_paths.append(Path(f"{file_path.parent}/{base_name}{original_extension}.json"))

    #Simply replace extension with json
    potential_paths.append(Path(f"{file_path.parent}/{base_name}.json"))

    #Live photo MOV or MP4
    if original_extension.lower().endswith(('.mov', '.mp4')):
        potential_paths.append(Path(f"{file_path.parent}/{base_name}.JPG.json"))
        potential_paths.append(Path(f"{file_path.parent}/{base_name}.HEIC.json"))
        potential_paths.append(Path(f"{file_path.parent}/{base_name}.jpeg.json"))

    # Check for (n) suffix
    match = re.search(r'(.*?)(\(\d+\))$', base_name)
    if match:
        main_part = match.group(1)
        suffix = match.group(2)
        if original_extension.lower().endswith(('.mov', '.mp4')):
            potential_paths.append(Path(f"{file_path.parent}/{main_part}.JPG{suffix}.json"))
            potential_paths.append(Path(f"{file_path.parent}/{main_part}.jpg{suffix}.json"))
            potential_paths.append(Path(f"{file_path.parent}/{main_part}.HEIC{suffix}.json"))
            potential_paths.append(Path(f"{file_path.parent}/{main_part}.jpeg{suffix}.json"))
            potential_paths.append(Path(f"{file_path.parent}/{main_part}{original_extension}{suffix}.json"))
        else:
            potential_paths.append(Path(f"{file_path.parent}/{main_part}{original_extension}{suffix}.json"))

        
    # Check if the main part (without suffix) is 46 characters or more
    if len(base_name) >= 46:
        potential_paths.append(Path(f"{file_path.parent}/{base_name[:46]}.json"))
        main_part = f"{base_name}{original_extension}"
        potential_paths.append(Path(f"{file_path.parent}/{main_part[:47]}.json"))

    # Check for -edited suffix
    if base_name.endswith('-edited'):
        new_base_name = base_name[:-7]  # Remove '-edited'
        potential_paths.append(Path(f"{file_path.parent}/{new_base_name}{original_extension}.json"))

    # Check other potential paths
    for path in potential_paths:
        if path.exists():
            return path

    # If no file exists, return None
    return None

def get_timestamp_taken_from_json(input_data):
    # Check if input_data is a path to a file or a JSON string
    if os.path.isfile(input_data):
        with open(input_data, 'r') as f:
            data = json.load(f)
    else:
        data = json.loads(input_data)
    
    timestamp = int(data['photoTakenTime']['timestamp'])
    return timestamp

def convert_timestamp_to_string(timestamp):
    # Convert the timestamp to a datetime object
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    
    # Format the datetime object to the desired string format
    formatted_string = dt.strftime("%Y:%m:%d %H:%M:%S")
    
    return formatted_string

def get_created_date(file_path):
    file_path = str(file_path) #path to str
    if file_path.lower().endswith('.heic'):
        with Image.open(file_path) as img:
            exif = img.getexif()
            date_time_original = exif.get(36867)  # 36867 is the tag for DateTimeOriginal
            if not date_time_original:
                # Fallback to other date fields if DateTimeOriginal is not available
                date_time_original = exif.get(306)  # 306 is the tag for DateTime
                if not date_time_original:
                    print(f"No EXIF 'taken' date found for {file_path}")
                return date_time_original
    elif file_path.lower().endswith(('.jpg', '.jpeg')):
        date_time_original = get_exif_date_jpeg(file_path)
        return date_time_original
    elif not file_path.lower().endswith('.json'):
        json_path = get_json_path(file_path)
        if json_path:
            timestamp = get_timestamp_taken_from_json(json_path)
            date_time_original = convert_timestamp_to_string(timestamp)
            return date_time_original