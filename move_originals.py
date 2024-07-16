import os
import shutil

def process_folders(root_dir):
    
    for folder_path, _, files in os.walk(root_dir):
        originals_folder = os.path.join(folder_path, "Originals")
        
        # Get all edited files, ignoring case
        edited_files = [f for f in files if f.lower().endswith('-edited' + os.path.splitext(f.lower())[1])]
        
        for edited_file in edited_files:
            # Find the corresponding original file
            file_name, file_ext = os.path.splitext(edited_file)
            original_file = file_name[:-7] + file_ext  # Remove '-edited' part
            
            if original_file in files:
                # Create Originals folder if it doesn't exist
                if not os.path.exists(originals_folder):
                    os.makedirs(originals_folder)
                
                # Move the original file to the Originals folder
                original_path = os.path.join(folder_path, original_file)
                destination_path = os.path.join(originals_folder, original_file)
                shutil.move(original_path, destination_path)
                print(f"Moved {original_file} to {originals_folder}")

if __name__ == "__main__":
    root_folder = "/Volumes/Ady_2tb_red/takeout_extract3/Takeout/Google Photos"
    process_folders(root_folder)