import os
import re
import imghdr
from pathlib import Path
from json_helper import *

def check_jpeg_and_json(directory):
    count=media_count=0
    for root, dirs, files in os.walk(directory):
        for file in files:
            count+=1
            if not file.lower().endswith('.json'):
                media_count+=1
                file_path = Path(root) / file
                json_path = get_json_path(file_path)
                try:
                    # Check if the file is actually a JPEG
                    #if imghdr.what(file_path) == 'jpeg':
                        #print(f"JPEG file with HEIC extension found: {file_path}")
                    
                    # Check for the sidecar JSON file
                    if not json_path or not json_path.exists():
                        print(f"Warning: Sidecar JSON file not found for {file_path}\n")
                        print(f"Looked for {json_path}")
                    #else:
                        #print(f"Sidecar JSON file found: {json_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    print(f"Checked {count} files of which {media_count} were media.")


# Usage
if __name__ == "__main__":
    takeout_path = "/Volumes/Ady_2tb_red/takeout_extract5/Takeout/Google_Photos"
    check_jpeg_and_json(takeout_path)