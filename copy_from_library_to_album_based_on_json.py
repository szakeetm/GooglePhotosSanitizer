import os
import json
from datetime import datetime, timedelta
from json_helper import *
import shutil

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
                    f"{image_basename}-edited.jpg",
                    f"{image_basename[:47]}{image_ext}"  # New truncated filename
                ]
                
                image_exists = any(os.path.exists(os.path.join(root, fname)) for fname in possible_filenames)
                
                if not image_exists:
                    timestamp = album_json['photoTakenTime']['timestamp']
                    date = datetime.utcfromtimestamp(int(timestamp))
                    year = date.year
                    
                    library_subfolder = f"Photos from {year}"
                    
                    json_basename, json_ext = os.path.splitext(file)
                    possible_json_names = [(file, 0)] + [(f"{json_basename}({i}){json_ext}", i) for i in range(1, 21)]

                    match_found = False
                    for json_name in possible_json_names:
                        library_json_path = os.path.join(library_folder, library_subfolder, json_name[0])
                        
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
                    else:
                        library_path = os.path.join(library_folder, library_subfolder)
                        image_found=False

                        # Generate the list of suffixes
                        suffixes = [""] + [f"({i})" for i in range(1, 21)]

                        # Generate filenames in the correct order
                        for suffix in suffixes:
                            possible_filenames.append(f"{image_basename}{suffix}.jpg")
                            possible_filenames.append(f"{image_basename}{suffix}.jpeg")
                            possible_filenames.append(f"{image_basename}{suffix}.heic")

                        # Add the original image filename at the end
                        possible_filenames.append(image_filename)

                        for image_fn_found in possible_filenames:
                            impath = os.path.join(library_path, image_fn_found)
                            if os.path.exists(impath):
                               imdate_str=get_created_date(impath)
                               imdate_datetime=datetime.strptime(imdate_str, "%Y:%m:%d %H:%M:%S")
                               # Set a margin of error (e.g., 2 hours)
                               margin = timedelta(hours=13)
    
                               # Assuming `date` is in the same timezone as `imdate_datetime`
                               if abs(imdate_datetime - date) <= margin:
                                image_found = True
                                break
                        
                        if not image_found:
                            print(f"Couldn't find {image_filename} in {library_subfolder}")
                        elif image_fn_found.lower().endswith(('.heic','.jpg','.jpeg')):
                            image_fn_basename, image_fn_ext = os.path.splitext(image_fn_found)
                            possible_live_photos = [
                                f"{image_fn_basename}.mov",
                                f"{image_fn_basename}.MOV",
                                f"{image_fn_basename}.mp4",
                                f"{image_fn_basename}.MP4"  # New truncated filename
                            ]

                            live_movie_found=False
                            for live_movie_fname in possible_live_photos:
                                live_movie_path=os.path.join(library_path, live_movie_fname)
                                if os.path.exists(live_movie_path):
                                    print(f"Found {live_movie_fname} for {image_fn_found} in {library_subfolder}")
                                    live_movie_found = True
                                    break

                            print(f"Copy {impath} to {root}")
                            # Copy the file to the destination folder
                            destination_file_path = os.path.join(root, os.path.basename(impath))
                            shutil.copy(impath, destination_file_path)
                            if live_movie_found:
                                print(f"Copy live movie {live_movie_path} to {root}")
                                # Copy the file to the destination folder
                                destination_file_path = os.path.join(root, os.path.basename(live_movie_path))
                                shutil.copy(live_movie_path, destination_file_path)
                    compared_files += 1
    
    return compared_files

def main():
    album_folder = "E:\\takeout_extract5\\Takeout\\Google_Photos\\Special_albums"
    library_folder = "E:\\takeout_extract5\\Takeout\\Google_Photos\\Library"
    
    total_compared = compare_json_files(album_folder, library_folder)
    print(f"Total JSON files compared: {total_compared}")

if __name__ == "__main__":
    main()