import os
import hashlib
from collections import defaultdict
from tee import *
import sys

def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def find_duplicates(root_folder):
    file_dict = defaultdict(list)
    
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if not filename.endswith('.json'):
                full_path = os.path.join(dirpath, filename)
                file_size = os.path.getsize(full_path)
                file_dict[(filename, file_size)].append(full_path)

    duplicates = defaultdict(list)
    
    for (filename, size), paths in file_dict.items():
        if len(paths) >= 3:
            hash_dict = defaultdict(list)
            for path in paths:
                file_hash = get_file_hash(path)
                hash_dict[file_hash].append(path)
            
            for hash_value, hash_paths in hash_dict.items():
                if len(hash_paths) >= 3:
                    duplicates[filename].extend(hash_paths)

    return duplicates

def main():
    root_folder = "E:\\takeout_extract4\\Takeout\\Google Photos"
    output_file = "triple_files_report.txt"

    # Redirect output to both console and file
    with open(output_file, 'w', encoding='utf-8') as f:
        original_stdout = sys.stdout
        sys.stdout = Tee(sys.stdout, f)

        duplicates = find_duplicates(root_folder)

        print(f"Scanning folder: {root_folder}")
        
        for dirpath, dirnames, filenames in os.walk(root_folder):
            print(f"\nEntering folder: {dirpath}")

        if not duplicates:
            print("\nNo duplicates found occurring 3 or more times.")
        else:
            print("\nDuplicates occurring 3 or more times:")
            for filename, paths in sorted(duplicates.items(), key=lambda x: x[1][0]):
                print(f"\nFile: {filename}")
                for path in sorted(paths):
                    print(f"  - {path}")

        # Restore original stdout
        sys.stdout = original_stdout

    print(f"\nReport saved to {output_file}")

if __name__ == "__main__":
    main()