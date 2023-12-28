import os
import re
from dateutil.parser import parse
import json
from dateutil import parser
from datetime import datetime


def get_pdf_files_in_directory(directory):
    """Get a list of PDF file paths from the specified directory."""
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.lower().endswith('.pdf')]

def extract_dates(text):
    current_date = datetime.now()
    minimum_age = 14  # Minimum age in years
    maximum_age = 80 

    date_patterns = [
       # Pattern 1: Matches dates in formats like DD/MM/YYYY, MM-DD-YYYY, YYYY.MM.DD
    r'\b(?:DOB|Date of Birth|BIRTH DATE|D\.O\.B\.|Birthdate|BrithDate):\s*(\d{2}[/.-]\d{2}[/.-]\d{4}|\d{4}[/.-]\d{2}[/.-]\d{2})\b',

    # Pattern 2: Matches dates in formats like Jan 23, 2020 or April 5, 1999
    r'\b(?:DOB|Date of Birth|BIRTH DATE|D\.O\.B\.|Birthdate|BrithDate):\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{1,2},\s\d{4})\b',

    # Pattern 3: Matches dates in formats like DD-MM-YY
    r'\b(?:DOB|Date of Birth|BIRTH DATE|D\.O\.B\.|Birthdate|BrithDate):\s*(\d{2}[/.-]\d{2}[/.-]\d{2})\b',

    # Pattern 4: Matches dates in formats like 23-MAR-2020 or March 23, 2020
    r'\b(?:DOB|Date of Birth|BIRTH DATE|D\.O\.B\.|Birthdate|BrithDate):\s*(\d{1,2}-[A-Z]{3}-\d{4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{1,2},\s\d{4})\b',

    # Pattern 5: Matches dates in formats like MM/YYYY
    r'\b(?:DOB|Date of Birth|BIRTH DATE|D\.O\.B\.|Birthdate|BrithDate):\s*(\d{2}/\d{4})\b'
    ]   

    # Making the regex more tolerant to variations and common misspellings
    prefix_pattern = prefix_pattern = r'^(DOB|Date of Birth|Birth Date|Birthdate):\s*'


    date_strings = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            cleaned_date = re.sub(prefix_pattern, '', match)
            date_strings.append(cleaned_date)

    parsed_dates = []
    for date_str in date_strings:
        try:
             # Handle MM/YYYY format separately
            if re.match(r'\d{2}/\d{4}', date_str):
                month, year = date_str.split('/')
                parsed_date = datetime(int(year), int(month), 1)  # Defaulting to the first day of the month
            else:
                parsed_date = parser.parse(date_str)

            # Age validation and formatting
            age = (current_date - parsed_date).days / 365.25
            if age >= minimum_age and is_valid_date(date_str):
                parsed_dates.append({
                "date": date_str,
                "age": round(age, 2),
                "year": parsed_date.year
                })
            # else:
            #     print(f"Excluded: {cleaned_date} (Age: {age:.2f} years)")
        except ValueError:
            cleaned_date

    return parsed_dates

def append_to_json_file(file_name, new_data):
    # Check if the file exists and is not empty
    if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:
        # Read existing data from the file
        with open(file_name, 'r') as file:
            data = json.load(file)
        # Append new data
        data.append(new_data)
    else:
        # If file doesn't exist or is empty, start with new data
        data = [new_data]

    # Write updated data back to the file
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)
        
def is_valid_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False       
        
