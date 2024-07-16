import os
from PIL import Image
from pillow_heif import register_heif_opener
from datetime import datetime
import subprocess
from jpeg_helper import *
from json_helper import *

# Register HEIF opener
register_heif_opener()

def parse_date_string(date_string):
    """Parse the date string into a datetime object."""
    try:
        return datetime.strptime(date_string, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        print(f"Error parsing date string: {date_string}")
        return None

def set_video_metadata(video_path, date_time_str):
    """Set the 'date taken' EXIF and 'file modified' date for a video file."""
    date_time = parse_date_string(date_time_str)
    if not date_time:
        return

    # Set 'date taken' EXIF metadata
    subprocess.run(['exiftool', '-overwrite_original', '-CreateDate=' + date_time_str, '-ModifyDate=' + date_time_str, video_path])
    
    # Set 'file modified' date
    os.utime(video_path, (datetime.now().timestamp(), date_time.timestamp()))

def check_images_in_subfolders(root_folder):
    """Walk through subfolders and check HEIC files for EXIF 'taken' date."""
    
    for subdir, _, files in os.walk(root_folder):
        print(f"Entering folder {subdir}...")
        for file in files:
            if file.lower().endswith('.heic'):
                file_path = os.path.join(subdir, file)
                date_time_original = get_exif_date(file_path)
                
                if date_time_original:
                    # Look for sidecar movie files
                    base_name = os.path.splitext(file)[0]
                    for ext in ['.mp4', '.MP4', '.mov', '.MOV']:
                        video_path = os.path.join(subdir, base_name + ext)
                        if os.path.exists(video_path):
                            print(f"Found sidecar video: {video_path}")
                            print(f"DateTimeOriginal for {file_path}: {date_time_original}")
                            set_video_metadata(video_path, date_time_original)

if __name__ == "__main__":
    root_folder = "/Volumes/Ady_2tb_red/takeout_extract5/Takeout/Google_Photos/"
    #root_folder = "/Users/martonady/Downloads/test"
    check_images_in_subfolders(root_folder)