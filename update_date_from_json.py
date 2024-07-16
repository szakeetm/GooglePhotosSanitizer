import os
from PIL import Image
import pillow_heif
from pillow_heif import register_heif_opener
import re
import imghdr
from pathlib import Path
from json_helper import *
from jpeg_helper import *
import subprocess

register_heif_opener()

def parse_date_string(date_string):
    """Parse the date string into a datetime object."""
    try:
        return datetime.strptime(date_string, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        print(f"Error parsing date string: {date_string}")
        return None

def set_media_metadata(media_path, date_time_str):
    """Set the 'date taken' EXIF and 'file modified' date for a video file."""
    date_time = parse_date_string(date_time_str)
    if not date_time:
        return

    # Set 'date taken' EXIF metadata
    if not str(media_path).lower().endswith(('.jpg','.jpeg','.heic')):
        pass
        #subprocess.run(['exiftool', '-overwrite_original', '-CreateDate=' + date_time_str, '-ModifyDate=' + date_time_str, media_path])
    
    # Set 'file modified' date
    os.utime(media_path, (date_time.timestamp(), date_time.timestamp()))

def modified_before_july_2024(file_path):
    # Get the last modified time
    modified_time = os.path.getmtime(file_path)

    # Convert the modified time to a datetime object
    modified_date = datetime.fromtimestamp(modified_time)

    # Define the cutoff date (July 1, 2024)
    cutoff_date = datetime(2024, 7, 1)

    # Check if the modified date is before the cutoff date
    is_before_2024 = modified_date < cutoff_date

    return is_before_2024
    

        


def check_json(directory):
    count=0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            if not file.lower().endswith('.json') and not modified_before_july_2024(file_path): #not yet updated
                date_time_original = get_created_date(file_path)
                if date_time_original:
                    set_media_metadata(file_path,date_time_original)
                    count+=1
                    print(f"{file_path} date set to {date_time_original}")
    print(f"Modified {count} files.")


# Usage
if __name__ == "__main__":
    takeout_path = "E:\\takeout_extract6\\Takeout\\Google_Photos"
    #takeout_path = "/Users/martonady/Downloads/test"
    check_json(takeout_path)