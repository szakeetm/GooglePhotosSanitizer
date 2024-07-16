import os
import shutil
import json
from datetime import datetime
import pytz
from PIL import Image
from PIL.ExifTags import TAGS
import piexif
from pillow_heif import register_heif_opener, HeifImagePlugin

register_heif_opener()

def get_exif_date(image_path):
    try:
        with Image.open(image_path) as img:
            if image_path.lower().endswith(('.jpg', '.jpeg', '.tiff', '.tif')):
                exif = {TAGS[k]: v for k, v in img._getexif().items() if k in TAGS}
                date_str = exif.get('DateTimeOriginal', '')
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            else:  # For HEIC and other formats
                exif = img.getexif()
                date_time_original = exif.get(36867)  # 36867 is the tag for DateTimeOriginal
                if date_time_original:
                    return datetime.strptime(date_time_original, '%Y:%m:%d %H:%M:%S')

                # Fallback to other date fields if DateTimeOriginal is not available
                date_time = exif.get(306)  # 306 is the tag for DateTime
                if date_time:
                    return datetime.strptime(date_time, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Can't get EXIF date for {image_path}: {str(e)}")
    return None

def set_exif_date(image_path, date):
    date_str = date.strftime("%Y:%m:%d %H:%M:%S")
    if image_path.lower().endswith(('.jpg', '.jpeg', '.tiff', '.tif')):
        try:
            exif_dict = piexif.load(image_path)
            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = date_str
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, image_path)
            print(f"Updated EXIF date for {image_path}")
        except Exception as e:
            print(f"Could not set EXIF date for {image_path}: {str(e)}")
    elif image_path.lower().endswith('.heic'):
            print(f"Skipping EXIF set for HEIC file: {image_path}")
    else:
        set_file_modification_time(image_path, date)

def set_file_modification_time(file_path, timestamp):
    os.utime(file_path, (timestamp, timestamp))
    print(f"Updated file modification time for {file_path}")

def get_json_photo_taken_time(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    timestamp = int(data['photoTakenTime']['timestamp'])
    return datetime.fromtimestamp(timestamp, pytz.UTC)

def find_matching_file(yearly_folder, filename, target_date):
    for root, _, files in os.walk(yearly_folder):
        if filename in files:
            file_path = os.path.join(root, filename)
            file_date = try_to_get_date(file_path)
            if file_date and file_date == target_date:
                return file_path
    return None

def copy_sidecar_mp4(src_folder, dest_folder, filename, target_date):
    base_name = os.path.splitext(filename)[0]
    mp4_filename = f"{base_name}.mp4"
    
    src_path = find_matching_file(src_folder, filename, target_date)
    if src_path:
        mp4_src_path = os.path.join(os.path.dirname(src_path), mp4_filename)
        if os.path.exists(mp4_src_path):
            dest_path = os.path.join(dest_folder, mp4_filename)
            if (not os.path.exists(dest_path)):
                shutil.copy2(mp4_src_path, dest_path)
                print(f"Copied {mp4_filename} to {dest_folder}")

def try_to_get_date(image_path):
    date = get_exif_date(image_path)
    
    if not date:
        # Check if the file name ends with "-edited" before the extension
        base_name, extension = os.path.splitext(image_path)
        if base_name.lower().endswith('-edited'):
            # Remove "-edited" from the base name
            base_name = base_name[:-7]  # -7 is the length of "-edited"
            json_path = f"{base_name}{extension}.json"
        else:
            json_path = f"{image_path}.json"
        
        if os.path.exists(json_path):
            date = get_json_photo_taken_time(json_path)
    
    return date

def process_albums(root_folder):
    for album_folder in os.listdir(root_folder):
        if album_folder.startswith("Photos from "):
            continue
        
        album_path = os.path.join(root_folder, album_folder)
        if not os.path.isdir(album_path):
            continue
        
        print(f"Processing album: {album_folder}")
        for filename in os.listdir(album_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.tiff')):
                image_path = os.path.join(album_path, filename)
                date = try_to_get_date(image_path)
                
                if date:
                    year = date.year
                    yearly_folder = os.path.join(root_folder, f"Photos from {year}")
                    if os.path.exists(yearly_folder):
                        copy_sidecar_mp4(yearly_folder, album_path, filename, date)
                else:
                    print(f"Could not determine date for {filename}")

if __name__ == "__main__":
    root_folder = "./"
    process_albums(root_folder)