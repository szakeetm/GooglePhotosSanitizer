import os
import json
import subprocess
import math

def read_json(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
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

def decimal_to_dms(degree):
    d = int(degree)
    m = int((degree - d) * 60)
    s = (degree - d - m / 60) * 3600
    return d, m, s

def format_dms(degree, ref):
    d, m, s = decimal_to_dms(abs(degree))
    return f"{d} deg {m}' {s:.2f}\" {ref}"

def write_gps_to_exif(file_path, gps_data):
    """Write GPS coordinates to metadata of a video file using exiftool."""
    lat = gps_data['latitude']
    lon = gps_data['longitude']
    alt = gps_data['altitude']

    lat_ref = 'N' if lat >= 0 else 'S'
    lon_ref = 'E' if lon >= 0 else 'W'

    gps_coordinates = f"{format_dms(lat, lat_ref)}, {format_dms(lon, lon_ref)}"

    command = [
        'exiftool',
        '-Keys:GPSCoordinates=' + gps_coordinates,
        '-overwrite_original',
        '-P',  # This option preserves the file's original modification date/time
        file_path
    ]

    # Execute exiftool command
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"GPS coordinates written to metadata for {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error writing GPS data to {file_path}: {e.stderr}")

def check_gps_in_metadata(file_path):
    """Check if valid GPS coordinates exist in metadata using exiftool."""
    command = ['exiftool', '-json', '-GPS:GPSLatitude', '-GPS:GPSLongitude', '-GPS:GPSAltitude', file_path]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        metadata = json.loads(result.stdout)[0]
        
        lat = metadata.get('GPSLatitude')
        lon = metadata.get('GPSLongitude')
        alt = metadata.get('GPSAltitude')
        
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

def get_json_path_video(file_path):
    """Get the path of the corresponding JSON sidecar file."""
    return file_path + '.json'

def check_videos_in_subfolders(root_folder):
    """Walk through subfolders and check video files for GPS coordinates."""
    video_extensions = ('.heic', '.mov', '.mp4', '.3gp', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v')
    
    for subdir, _, files in os.walk(root_folder):
        print(f"Entering folder {subdir}...")
        for file in files:
            if file.lower().endswith(video_extensions):
                file_path = os.path.join(subdir, file)
                
                if check_gps_in_metadata(file_path):
                    pass
                    #print(f"Valid GPS coordinates found in metadata for {file_path}")
                else:
                    #print(f"No valid GPS coordinates found in metadata for {file_path}")
                    json_path = get_json_path_video(file_path)
                    
                    if json_path and os.path.exists(json_path):
                        gps_data = get_gps_from_json(json_path)
                        if gps_data:
                            print(f"Valid GPS coordinates found in JSON for {file_path}")
                            write_gps_to_exif(file_path, gps_data)
                        else:
                            pass
                            #print(f"No valid GPS coordinates found in JSON for {file_path}")
                    else:
                        pass
                        #print(f"No JSON sidecar found for {file_path}")

if __name__ == "__main__":
    root_folder = "E:\\takeout_extract6\\Takeout\\Google_Photos\\Special_albums"
    check_videos_in_subfolders(root_folder)