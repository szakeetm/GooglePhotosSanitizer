import os
from PIL import Image
import piexif
from datetime import datetime, timezone

def write_date_to_exif(file_path, utc_timestamp):
    """Write the given date to the EXIF data of a JPEG file."""
    try:
        # Convert UTC timestamp to datetime object
        date_taken = datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)
        
        # Convert datetime to the required EXIF format
        date_string = date_taken.strftime("%Y:%m:%d %H:%M:%S")
        
        # Load existing EXIF data
        exif_dict = piexif.load(file_path)
        
        # Convert date_string to bytes
        date_bytes = date_string.encode('utf-8')
        
        # Update the EXIF dictionary
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_bytes
        
        # Convert the EXIF dictionary to bytes
        exif_bytes = piexif.dump(exif_dict)
        
        # Write the updated EXIF data to the file
        piexif.insert(exif_bytes, file_path)
        
        print(f"Date written to EXIF for {file_path}: {date_string}")
    except Exception as e:
        print(f"Error writing EXIF to {file_path}: {str(e)}")

import piexif
from datetime import datetime
from pathlib import Path

def get_exif_date_jpeg(file_path: Path) -> str:
    """Extract DateTimeOriginal from EXIF data of a JPEG file."""
    try:
        exif_dict = piexif.load(str(file_path))
        if "Exif" in exif_dict:
            date_time_original = exif_dict["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
            if date_time_original:
                date_str = date_time_original.decode('utf-8')
                # Verify and format the date
                try:
                    # Handle the case with timezone
                    if '+' in date_str or '-' in date_str[19:]:
                        date_obj = datetime.fromisoformat(date_str)
                    else:
                        date_obj = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                    return date_obj.strftime("%Y:%m:%d %H:%M:%S")
                except ValueError:
                    print(f"Invalid date format in EXIF for {file_path}: {date_str}")
                    return None
        return None
    except Exception as e:
        print(f"Error reading EXIF from {file_path}: {str(e)}")
        return None