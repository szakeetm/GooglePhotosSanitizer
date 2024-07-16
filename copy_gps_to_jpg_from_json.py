import os
import json
import subprocess
from jpeg_helper import *
from json_helper import *

def read_json(json_path):
    """Read and parse a JSON file."""
    try:
        with open(json_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Error decoding JSON file: {json_path}")
        return None
    except IOError:
        print(f"Error reading JSON file: {json_path}")
        return None

def get_gps_from_json(json_path):
    """Extract GPS coordinates from JSON file."""
    json_data = read_json(json_path)
    if 'geoData' in json_data:
        lat = json_data['geoData']['latitude']
        lon = json_data['geoData']['longitude']
        alt = json_data['geoData']['altitude']
        
        # Check if coordinates are all zero
        if lat == 0 and lon == 0 and alt == 0:
            return None
        
        return {
            'latitude': lat,
            'longitude': lon,
            'altitude': alt
        }
    return None

def write_gps_to_exif(file_path, gps_data):
    """Write GPS coordinates to EXIF data of an image using exiftool."""
    lat = gps_data['latitude']
    lon = gps_data['longitude']
    alt = gps_data['altitude']

    lat_ref = 'N' if lat >= 0 else 'S'
    lon_ref = 'E' if lon >= 0 else 'W'

    # Prepare exiftool command
    command = [
        'exiftool',
        '-GPSLatitude=' + str(abs(lat)),
        '-GPSLatitudeRef=' + lat_ref,
        '-GPSLongitude=' + str(abs(lon)),
        '-GPSLongitudeRef=' + lon_ref,
        '-GPSAltitude=' + str(alt),
        '-overwrite_original',
        file_path
    ]

    # Execute exiftool command
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"GPS coordinates written to EXIF for {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error writing GPS data to {file_path}: {e.stderr}")

def check_gps_in_exif(file_path):
    """Check if valid GPS coordinates exist in EXIF data using exiftool."""
    command = ['exiftool', '-json', '-GPS:GPSLatitude', '-GPS:GPSLongitude', '-GPS:GPSAltitude', file_path]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        exif_data = json.loads(result.stdout)[0]
        
        lat = exif_data.get('GPSLatitude')
        lon = exif_data.get('GPSLongitude')
        alt = exif_data.get('GPSAltitude')
        
        # Check if coordinates exist and are not all zero
        if lat and lon and alt:
            def parse_coordinate(coord):
                try:
                    return float(coord.split()[0])
                except (ValueError, AttributeError):
                    return None

            lat_value = parse_coordinate(lat)
            lon_value = parse_coordinate(lon)
            alt_value = parse_coordinate(alt)
            
            if lat_value is not None and lon_value is not None and alt_value is not None:
                if lat_value != 0 or lon_value != 0 or alt_value != 0:
                    return True
        
        return False
    except subprocess.CalledProcessError:
        return False

def check_images_in_subfolders(root_folder):
    """Walk through subfolders and check JPEG files for GPS coordinates."""
    
    for subdir, _, files in os.walk(root_folder):
        print(f"Entering folder {subdir}...")
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg')):
                file_path = os.path.join(subdir, file)
                
                if check_gps_in_exif(file_path):
                    pass
                    #print(f"Valid GPS coordinates found in EXIF for {file_path}")
                else:
                    #print(f"No valid GPS coordinates found in EXIF for {file_path}")
                    json_path = get_json_path(file_path)
                    
                    if json_path and os.path.exists(json_path):
                        gps_data = get_gps_from_json(json_path)
                        if gps_data:
                            print(f"Valid GPS coordinates found in JSON for {file_path}")
                            write_gps_to_exif(file_path, gps_data)
                        else:
                            pass
                            #print(f"No valid GPS coordinates found in JSON for {file_path}")
                    else:
                        print(f"No JSON sidecar found for {file_path}")

if __name__ == "__main__":
    #root_folder = "E:\\takeout_extract5\\Takeout\\Google_Photos"
    root_folder = "/Volumes/Ady_2tb_red/takeout_extract5/Takeout/Google_Photos/Regular_albums"
    check_images_in_subfolders(root_folder)