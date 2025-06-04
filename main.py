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
date_pattern3 = re.compile(r'\d{8}-\d{4}-\d{2}-\d{2}')

def is_ambiguous(date_str):
    """Check if a date string can be interpreted in multiple valid ways."""
    # Try interpreting as YYYYMMDD
    try:
        date1 = datetime.strptime(date_str, "%Y%m%d").date()
    except ValueError:
        date1 = None
    # Try interpreting as YYYYDDMM
    try:
        date2 = datetime.strptime(date_str, "%Y%d%m").date()
    except ValueError:
        date2 = None
    # Ambiguous if both interpretations are valid and result in different dates
    return date1 and date2 and date1 != date2

def subtracter(execution_date, file_date):
    """Calculate the difference in days between two dates."""
    return (execution_date - file_date).days

def extract_date_from_filename(filename):
    """Extract date object from filename if it contains a valid date format."""
    match = date_pattern.search(filename) or date_pattern2.search(filename) or date_pattern3.search(filename)
    
    if match:
        date_str = match.group()
        try:
            if '-' in date_str and len(date_str) == 17: 
                compact, hyphenated = date_str.split('-')
                date1 = datetime.strptime(compact, "%Y%m%d").date()
                date2 = datetime.strptime(hyphenated, "%Y-%m-%d").date()
                return date1, date2
            elif '-' in date_str:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                if is_ambiguous(date_str):
                    return "ambiguous"
                return datetime.strptime(date_str, "%Y%m%d").date()
        except ValueError:
            pass
    else:
        pass
    
    return None

def sort_files_by_date_diff(date_diff, filename, invalid_files, valid_files, ambiguous_files, invalid_file_path, ambiguous_file_path):
    """Classify files into valid, invalid or ambiguous based on date difference."""
    if date_diff == "ambiguous":
        ambiguous_files.append(filename)
        try:
            shutil.move(os.path.join(file_directory, filename), ambiguous_file_path)
        except shutil.Error:
            pass
    elif date_diff > 5:
        invalid_files.append(filename)
        try:
            shutil.move(os.path.join(file_directory, filename), invalid_file_path)
        except shutil.Error:
            pass
    else:
        valid_files.append(filename)

    return valid_files, invalid_files, ambiguous_files

def display_results(valid_files, invalid_files, ambiguous_files):
    """Print categorized results to console."""
    print(Fore.GREEN + "FILES WHICH ARE VALID:" + Style.RESET_ALL)
    for file in valid_files:
        print("✅", file)
        time.sleep(1)
    
    print("\n" + Fore.YELLOW + "FILES MOVED TO AMBIGUOUS FOLDER:" + Style.RESET_ALL)
    for file in ambiguous_files:
        print("❓", file)
        time.sleep(1)
    
    print("\n" + Fore.RED + "FILES MOVED TO INVALID FOLDER:" + Style.RESET_ALL)
    for file in invalid_files:
        print("❌", file)
        time.sleep(1)

    print("\nSummary:")
    print("Valid files:", len(valid_files))
    print("Ambiguous files:", len(ambiguous_files))
    print("Invalid files:", len(invalid_files))

if __name__ == "__main__":
    # Set paths and initialize lists
    file_directory = "test_files"
    invalid_file_path = 'invalid'
    ambiguous_file_path = 'ambiguous'
    current_date = date.today()
    
    # Create directories if they don't exist
    os.makedirs(invalid_file_path, exist_ok=True)
    os.makedirs(ambiguous_file_path, exist_ok=True)
    
    valid_files = []
    invalid_files = []
    ambiguous_files = []

    # Process each file
    try:
        files = os.listdir(file_directory)
        for file in files:
            file_date = extract_date_from_filename(file)
            if file_date:
                if file_date == "ambiguous":
                    sort_files_by_date_diff("ambiguous", file, invalid_files, valid_files, ambiguous_files, invalid_file_path, ambiguous_file_path)
                elif isinstance(file_date, tuple):
                    # Handle the case where two dates were found
                    date_diff1 = subtracter(current_date, file_date[0])
                    date_diff2 = subtracter(current_date, file_date[1])
                    # Use the smaller difference
                    date_diff = min(date_diff1, date_diff2)
                    sort_files_by_date_diff(date_diff, file, invalid_files, valid_files, ambiguous_files, invalid_file_path, ambiguous_file_path)
                else:
                    date_diff = subtracter(current_date, file_date)
                    sort_files_by_date_diff(date_diff, file, invalid_files, valid_files, ambiguous_files, invalid_file_path, ambiguous_file_path)
            else:
                invalid_files.append(file)
                try:
                    shutil.move(os.path.join(file_directory, file), invalid_file_path)
                except shutil.Error:
                    pass
    except FileNotFoundError:
        print(f"Directory not found: {file_directory}")
    
    # Display final results
    display_results(valid_files, invalid_files, ambiguous_files)