import os
from PIL import Image
from pillow_heif import register_heif_opener

# Register HEIC opener for Pillow
register_heif_opener()

def rename_heic_to_jpg(root_path):
    """
    Recursively renames HEIC files to JPG if they are valid JPEG images.
    :param root_path: Root directory to start scanning.
    """
    for dirpath, _, filenames in os.walk(root_path):
        for file in filenames:
            if file.lower().endswith('.heic'):
                file_path = os.path.join(dirpath, file)
                try:
                    # Open the HEIC file
                    with Image.open(file_path) as img:
                        # Check if the image can be converted to RGB (JPEG-compatible)
                        img.verify()  # Verify image integrity
                        # Rename the file with .jpg extension
                        new_file_path = os.path.join(dirpath, f"{os.path.splitext(file)[0]}.jpg")
                        os.rename(file_path, new_file_path)
                        print(f"Renamed: {file_path} -> {new_file_path}")
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")

# Example usage:
# Replace '/path/to/directory' with your target directory
rename_heic_to_jpg('/Volumes/Ady_1Tb/pcloud/Photos/Marci Albumok')
