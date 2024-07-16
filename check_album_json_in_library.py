import os
import json
from datetime import datetime

def compare_json_files(album_folder, library_folder):
    compared_files = 0
    
    for root, dirs, files in os.walk(album_folder):
        for file in files:
            if file.endswith('.json') and not file.startswith('metadata'):
                album_json_path = os.path.join(root, file)
                
                try:
                    with open(album_json_path, 'r', encoding='utf-8') as f:
                        album_json = json.load(f)
                except UnicodeDecodeError:
                    print(f"Error reading {album_json_path}. Skipping this file.")
                    continue
                
                image_filename = album_json.get('title')
                image_basename, image_ext = os.path.splitext(image_filename)
                
                possible_filenames = [
                    image_filename,
                    f"{image_basename}.jpg",
                    f"{image_basename}-edited{image_ext}",
                    f"{image_basename}-edited.jpg"
                ]
                
                image_exists = any(os.path.exists(os.path.join(root, fname)) for fname in possible_filenames)
                
                if not image_exists:
                    timestamp = album_json['photoTakenTime']['timestamp']
                    date = datetime.utcfromtimestamp(int(timestamp))
                    year = date.year
                    
                    library_subfolder = f"Photos from {year}"
                    
                    json_basename, json_ext = os.path.splitext(file)
                    possible_json_names = [file] + [f"{json_basename}({i}){json_ext}" for i in range(1, 21)]
                    
                    match_found = False
                    for json_name in possible_json_names:
                        library_json_path = os.path.join(library_folder, library_subfolder, json_name)
                        
                        if os.path.exists(library_json_path):
                            try:
                                with open(library_json_path, 'r', encoding='utf-8') as f:
                                    library_json = json.load(f)
                            except UnicodeDecodeError:
                                print(f"Error reading {library_json_path}. Skipping this file.")
                                continue
                            
                            # Compare JSONs ignoring imageViews and all of creationTime
                            def filter_json(json_dict):
                                return {k: v for k, v in json_dict.items() if k != 'imageViews' and k != 'creationTime' and k != 'url'}
                            
                            album_json_compare = filter_json(album_json)
                            library_json_compare = filter_json(library_json)
                            
                            if album_json_compare == library_json_compare:
                                match_found = True
                                break
                    
                    if not match_found:
                        print(f"No matching JSON found for {file} in {root}")
                        print(f"Library folder: {os.path.join(library_folder, library_subfolder)}")
                    
                    compared_files += 1
    
    return compared_files

def main():
    album_folder = "E:\\takeout_extract5\\Takeout\\Google_Photos\\Regular_albums"
    library_folder = "E:\\takeout_extract5\\Takeout\\Google_Photos\\Library"
    
    total_compared = compare_json_files(album_folder, library_folder)
    print(f"Total JSON files compared: {total_compared}")

if __name__ == "__main__":
    main()