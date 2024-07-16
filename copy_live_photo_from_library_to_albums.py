import os
import shutil

def link_sidecar_movies(library_folder, albums_folder, dry_run=False):
    # Dictionaries to store files in the library
    library_images = {}
    library_movies = {}

    # Scan the library folder for image and movie files
    print(f"Scanning library folder: {library_folder}")
    for root, dirs, files in os.walk(library_folder):
        print(f"Entering directory: {root}")
        for file in files:
            lower_file = file.lower()
            full_path = os.path.join(root, file)
            base_name = os.path.splitext(file)[0]
            file_size = os.path.getsize(full_path)

            if lower_file.endswith(('.jpg', '.jpeg', '.heic')):
                library_images[(base_name, file_size)] = (full_path, root)
            elif lower_file.endswith(('.mp4', '.mov')):
                library_movies[base_name] = (full_path, root)

    linked_count = 0
    duplicate_count = 0

    # Scan the albums folder
    for album_name in os.listdir(albums_folder):
        print(f"Scanning {album_name}...")
        album_path = os.path.join(albums_folder, album_name)
        if os.path.isdir(album_path):
            for file in os.listdir(album_path):
                lower_file = file.lower()
                if lower_file.endswith(('.jpg', '.jpeg', '.heic')):
                    album_image_path = os.path.join(album_path, file)
                    base_name = os.path.splitext(file)[0]
                    file_size = os.path.getsize(album_image_path)
                    
                    # Check if there's a duplicate image in the library
                    if (base_name, file_size) in library_images:
                        duplicate_count += 1
                        library_image, library_folder = library_images[(base_name, file_size)]
                        if dry_run:
                            print(f"Would delete {library_image} as it matches {album_image_path}")
                        else:
                            os.remove(library_image)
                            print(f"Deleted {library_image} as it matches {album_image_path}")
                        
                        # Check for corresponding movie file in the same folder
                        for movie_ext in ['.mp4', '.mov']:
                            potential_movie = os.path.join(library_folder, f"{base_name}{movie_ext}")
                            if os.path.exists(potential_movie):
                                album_movie = os.path.join(album_path, os.path.basename(potential_movie))
                                
                                if not os.path.exists(album_movie):
                                    if dry_run:
                                        print(f"Would move: {potential_movie} -> {album_movie}")
                                        linked_count += 1
                                    else:
                                        try:
                                            shutil.move(potential_movie, album_movie)
                                            print(f"Moved: {potential_movie} -> {album_movie}")
                                            linked_count += 1
                                        except OSError as e:
                                            print(f"Error moving {potential_movie}: {e}")
                                
                                break  # Stop searching after finding a matching movie

    return linked_count, duplicate_count

# Example usage
library_folder = "E:\\takeout_extract4\\Takeout\\Google_Photos\\Library"
albums_folder = "E:\\takeout_extract4\\Takeout\\Google_Photos\\Special_albums"

# Dry run
#print("Dry run:")
#potential_links, potential_duplicates = link_sidecar_movies(library_folder, albums_folder, dry_run=True)
#print(f"Total potential moves: {potential_links}")
#print(f"Total potential duplicates: {potential_duplicates}")

# Actual run
print("\nActual run:")
created_links, found_duplicates = link_sidecar_movies(library_folder, albums_folder, dry_run=False)
print(f"Total files moved: {created_links}")
print(f"Total duplicates found: {found_duplicates}")