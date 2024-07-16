import os
import json
from datetime import datetime

def compare_json_files(album_folder, library_folder):
    compared_files = 0
    
    for root, dirs, files in os.walk(album_folder):
        for file in files:
            if file.endswith('.json'):
                album_json_path = os.path.join(root, file)
                
                with open(album_json_path, 'r') as f:
                    album_json = json.load(f)
                
                image_filename = album_json.get('title')
                image_path = os.path.join(root, image_filename)
                image_path_jpg = os.path.splitext(image_path)[0] + '.jpg'
                
                # Only proceed if the image file doesn't exist in the album folder
                if not (os.path.exists(image_path) or os.path.exists(image_path_jpg)):
                    timestamp = album_json['photoTakenTime']['timestamp']
                    date = datetime.utcfromtimestamp(int(timestamp))
                    year = date.year
                    
                    library_subfolder = f"Photos from {year}"
                    library_json_path = os.path.join(library_folder, library_subfolder, file)
                    
                    if not os.path.exists(library_json_path):
                        print(f"JSON file {file} not found in {library_subfolder}")
                        continue
                    
                    with open(library_json_path, 'r') as f:
                        library_json = json.load(f)
                    
                    if album_json != library_json:
                        print(f"JSON content mismatch for {file}")
                        print(f"Album folder: {root}")
                        print(f"Library folder: {os.path.join(library_folder, library_subfolder)}")
                    
                    compared_files += 1
    
    return compared_files

def main():
    album_folder = "Regular_albums"
    library_folder = "Library"
    
    total_compared = compare_json_files(album_folder, library_folder)
    print(f"Total JSON files compared: {total_compared}")

if __name__ == "__main__":
    main()