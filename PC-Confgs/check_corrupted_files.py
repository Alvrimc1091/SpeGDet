# Script running in
# /home/alvaro/Documents/Workspace/Granos/FTP/check_corrupted_files.py


import os
import shutil

def find_corrupted_files(folder_path, destination_folder):
    try:
        # List to store corrupted files
        corrupted_files = []

        # Check each file in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Check if it's a file and if its size is 0 bytes
            if os.path.isfile(file_path) and os.path.getsize(file_path) == 0:
                corrupted_files.append(filename)
                # Move the corrupted file to the destination folder
                shutil.move(file_path, os.path.join(destination_folder, filename))
                print(f"Moved corrupted file: {filename} to {destination_folder}")


        # Print results
        if corrupted_files:
            print(f"Corrupted files (0 bytes) found in {folder_path} have been moved:")
            for file in corrupted_files:
                print(f" - {file}")
        else:
            print(f"\nNo corrupted files found in {folder_path}.")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Specify the folder path to check for corrupted files
    destination_folder = "/home/alvaro/Documents/Workspace/Granos/FTP/Corrupted_data"
    folder_to_check_luke = "/home/alvaro/Documents/Workspace/Granos/FTP/Data_luke"
    folder_to_check_leia = "/home/alvaro/Documents/Workspace/Granos/FTP/Data_leia"

    find_corrupted_files(folder_to_check_luke, destination_folder)
    find_corrupted_files(folder_to_check_leia, destination_folder)

if __name__ == "__main__":
     main()
