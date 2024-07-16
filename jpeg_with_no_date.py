import os
from PIL import Image
import piexif
from datetime import datetime
from jpeg_helper import *
from json_helper import *

def check_images_in_subfolders(root_folder):
    """Walk through subfolders and check JPEG files for EXIF 'taken' date."""
    
    for subdir, _, files in os.walk(root_folder):
        print(f"Entering folder {subdir}...")
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg')):
                file_path = os.path.join(subdir, file)
                date_time_original = get_exif_date(file_path)
                
                if date_time_original:
                    pass
                    # print(f"DateTimeOriginal for {file_path}: {date_time_original}")
                else:
                    print(f"No EXIF 'taken' date found for {file_path}")
                    write_date_to_exif(file_path,get_timestamp_taken_from_json(get_json_path(file_path)))

if __name__ == "__main__":
    root_folder = "/Volumes/Ady_2tb_red/takeout_extract5/Takeout/Google_Photos/"
    check_images_in_subfolders(root_folder)