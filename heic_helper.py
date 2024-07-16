import os
from PIL import Image
import pillow_heif
from pillow_heif import register_heif_opener

def convert_heic_to_jpeg(heic_path):
    # Register the HEIF opener with Pillow
    pillow_heif.register_heif_opener()

    # Generate the JPEG file path
    base_path = os.path.splitext(heic_path)[0]
    jpeg_path = base_path + '.jpg'

    # Open the HEIC image
    image = Image.open(heic_path)

    # Convert and save as JPEG
    image.convert('RGB').save(jpeg_path, 'JPEG')

    print(f"Converted {heic_path} to {jpeg_path}")

def get_exif_date_heic(file_path):
    """Extract EXIF date from an image file."""
    try:
        with Image.open(file_path) as img:
            exif = img.getexif()
            date_time_original = exif.get(36867)  # 36867 is the tag for DateTimeOriginal
            if not date_time_original:
                # Fallback to other date fields if DateTimeOriginal is not available
                date_time_original = exif.get(306)  # 306 is the tag for DateTime
                if not date_time_original:
                    print(f"No EXIF 'taken' date found for {file_path}")
            return date_time_original
    except Exception as e:
        print(f"Error reading EXIF from {file_path}: {str(e)}")
        return {}