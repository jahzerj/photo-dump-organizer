import os
import shutil
import re
import argparse
from pathlib import Path

def organize_photos(source_dir):
    # Check if source directory exists
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    # Pattern to match the date in filenames like PXL_20230507_060812369
    date_pattern = re.compile(r'PXL_(\d{4})(\d{2})\d{2}')
    
    # Dictionary to store folders already created
    created_folders = {}
    
    # Count for statistics
    moved_files = 0
    skipped_files = 0
    
    # Get all files in the source directory
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        # Try to match date pattern in filename
        match = date_pattern.search(filename)
        if match:
            year = match.group(1)
            month = match.group(2)
            target_folder_name = f"{year}.{month}"
            target_folder_path = os.path.join(source_dir, target_folder_name)
            
            # Create the target folder if it doesn't exist
            if target_folder_name not in created_folders:
                os.makedirs(target_folder_path, exist_ok=True)
                created_folders[target_folder_name] = True
                print(f"Created folder: {target_folder_name}")
            
            # Move the file to the target folder
            target_file_path = os.path.join(target_folder_path, filename)
            shutil.move(file_path, target_file_path)
            moved_files += 1
            print(f"Moved: {filename} -> {target_folder_name}/")
        else:
            skipped_files += 1
            print(f"Skipped: {filename} (doesn't match pattern)")
    
    print(f"\nSummary: Moved {moved_files} files, Skipped {skipped_files} files")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize photos into folders by year and month.")
    parser.add_argument("source_dir", help="Directory containing photos to organize")
    args = parser.parse_args()
    
    organize_photos(args.source_dir)

