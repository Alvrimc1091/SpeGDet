import os
from glob import glob

def get_last_two_files(directory, file_extension):
    # Use glob to find all files with the given extension
    files = glob(os.path.join(directory, f"*.{file_extension}"))
    
    # Sort files by their modification time in descending order
    files.sort(key=os.path.getmtime, reverse=True)
    
    # Return the last two files (or fewer if there are less than two)
    return files[:2]

def get_last_two_jpg_and_csv_files(directory):
    last_two_jpg_files = get_last_two_files(directory, "jpg")
    last_two_csv_files = get_last_two_files(directory, "csv")
    
    return last_two_jpg_files, last_two_csv_files

# Example usage:
directory_path = "/home/pi/SpeGDet/DataMeassures/TestMeassures"
last_two_jpg, last_two_csv = get_last_two_jpg_and_csv_files(directory_path)

print("Last two .jpg files:", last_two_jpg)
print("Last two .csv files:", last_two_csv)
