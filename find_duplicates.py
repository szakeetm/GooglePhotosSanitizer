import os
from collections import defaultdict

def find_and_replace_duplicates(library_folder, albums_folder, dry_run=False):
    library_files = defaultdict(list)

    # Scan the library folder and all its subfolders
    for root, _, files in os.walk(library_folder):
        for file in files:
            if not file.endswith('.json'):
                full_path = os.path.join(root, file)
                file_size = os.path.getsize(full_path)
                library_files[(file, file_size)].append(full_path)

    replacements = []

    # Scan the albums folder
    for album_name in os.listdir(albums_folder):
        album_path = os.path.join(albums_folder, album_name)
        if os.path.isdir(album_path):
            for file in os.listdir(album_path):
                if not file.endswith('.json'):
                    album_file_path = os.path.join(album_path, file)
                    file_size = os.path.getsize(album_file_path)
                    
                    # Check for duplicates by filename and size
                    if (file, file_size) in library_files:
                        library_file_path = library_files[(file, file_size)][0]
                        replacements.append((album_file_path, library_file_path))

    # Perform replacements
    for album_file, library_file in replacements:
        if dry_run:
            print(f"Would replace {album_file} with hardlink to {library_file}")
        else:
            try:
                os.remove(album_file)
                os.link(library_file, album_file)
                print(f"Replaced {album_file} with hardlink to {library_file}")
            except OSError as e:
                print(f"Error replacing {album_file}: {e}")

    return len(replacements)

# Example usage
library_folder = "E:\\takeout_extract4\\Takeout\\Google_Photos\\Library"
albums_folder = "E:\\takeout_extract4\\Takeout\\Google_Photos\\Regular_albums"
special_albums_folder = "E:\\takeout_extract4\\Takeout\\Google_Photos\\Special_albums"

# Dry run
print("Dry run:")
num_replacements = find_and_replace_duplicates(library_folder, albums_folder, dry_run=True)
print(f"Total potential replacements: {num_replacements}")

# Actual run
print("\nActual run:")
#num_replacements = find_and_replace_duplicates(library_folder, albums_folder, dry_run=False)
print(f"Total replacements made: {num_replacements}")