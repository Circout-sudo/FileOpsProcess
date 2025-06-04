import os
import re
import shutil
from datetime import date, datetime
from colorama import Fore, Style, init
import time

init()

# Regular expressions to detect dates in filenames
date_pattern = re.compile(r'\d{8}')
date_pattern2 = re.compile(r'\d{4}-\d{2}-\d{2}')

def subtracter(execution_date, file_date):
    """Calculate the difference in days between two dates."""
    return (execution_date - file_date).days

def extract_date_from_filename(filename):
    """Extract date object from filename if it contains a valid date format."""
    match = date_pattern.search(filename) or date_pattern2.search(filename)
    
    if match:
        date_str = match.group()
        try:
            if '-' in date_str:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                return datetime.strptime(date_str, "%Y%m%d").date()
        except ValueError:
            pass
    else:
        pass
    
    return None

def sort_files_by_date_diff(date_diff, filename, invalid_files, valid_files):
    """Classify files into valid or invalid based on date difference."""
    if date_diff > 5:
        invalid_files.append(filename)
    else:
        valid_files.append(filename)

    return valid_files, invalid_files

def display_results(valid_files, invalid_files, invalid_file_path):
    """Print categorized results to console."""
    print(Fore.GREEN + "VALID FILES:" + Style.RESET_ALL)
    for file in valid_files:
        print("✅", file)
        time.sleep(1)
    
    print("\n" + Fore.RED + "INVALID FILES:" + Style.RESET_ALL)
    for file in invalid_files:
        print("❌", file)
        try:
            shutil.move("test_files/" + file,invalid_file_path)
        except shutil.Error:
            print("")
        time.sleep(1)

    print("\nSummary:")
    print("Valid files:", len(valid_files))
    print("Invalid files:", len(invalid_files))

if __name__ == "__main__":
    # Set paths and initialize lists
    invalid_file_path = 'invalid'
    file_directory = "test_files"
    current_date = date.today()
    
    valid_files = []
    invalid_files = []

    # Process each file
    try:
        files = os.listdir(file_directory)
        for file in files:
            file_date = extract_date_from_filename(file)
            if file_date:
                date_difference = subtracter(current_date, file_date)
                sort_files_by_date_diff(date_difference, file, invalid_files, valid_files)
            else:
                invalid_files.append(file)
    except FileNotFoundError:
        print(f"Directory not found: {file_directory}")
    
    # Display final results
    display_results(valid_files, invalid_files, invalid_file_path)