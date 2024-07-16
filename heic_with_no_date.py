import os
from PIL import Image
import pillow_heif
from pillow_heif import register_heif_opener
from json_helper import *
import piexif
from datetime import datetime, timezone

def get_exif_data(image):
    """Extract EXIF data from a PIL Image."""
    try:
        exif = image.getexif()
        if exif is not None:
            return {
                Image.TAGS.get(tag, tag): value
                for tag, value in exif.items()
            }
        else:
            return {}
    except AttributeError:
        return {}

def check_images_in_subfolders(root_folder):
    """Walk through subfolders and check HEIC files for EXIF 'taken' date."""
    register_heif_opener()
    
    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith('.heic'):
                file_path = os.path.join(subdir, file)
                try:
                    with Image.open(file_path) as img:
                        exif = img.getexif()
                        date_time_original = exif.get(36867)  # 36867 is the tag for DateTimeOriginal
                        if not date_time_original:
                            # Fallback to other date fields if DateTimeOriginal is not available
                            date_time_original = exif.get(306)  # 306 is the tag for DateTime
                            if not date_time_original:
                                print(f"No EXIF 'taken' date found for {file_path}")
                                convert_heic_to_jpeg_with_exif(file_path)
                                
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

def convert_heic_to_jpeg_with_exif(heic_path):
    pillow_heif.register_heif_opener()

    # Generate the JPEG file path
    base_path = os.path.splitext(heic_path)[0]
    jpeg_path = base_path + '.jpg'

    # Open the HEIC image
    image = Image.open(heic_path)

    # Convert to RGB
    rgb_image = image.convert('RGB')

    # Get the JSON path and read the date taken
    json_path = get_json_path(heic_path)
    utc_timestamp = get_timestamp_taken_from_json(json_path)
    # Convert UTC timestamp to datetime object
    date_taken = datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)
    
    # Convert datetime to the required EXIF format
    date_string = date_taken.strftime("%Y:%m:%d %H:%M:%S")
    
    # Create EXIF data
    exif_dict = {"0th": {}, "Exif": {}}
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_string

    # Convert EXIF data to bytes
    exif_bytes = piexif.dump(exif_dict)

    # Save as JPEG with EXIF data
    rgb_image.save(jpeg_path, 'JPEG', exif=exif_bytes)

    print(f"Converted {heic_path} to {jpeg_path} with date taken: {date_taken}")

if __name__ == "__main__":
    #root_folder = "/Users/martonady/Downloads/test_ori"  # Replace with the path to your folder
    root_folder = "/Volumes/Ady_2tb_red/takeout_extract5/Takeout/Google_Photos"
    check_images_in_subfolders(root_folder)