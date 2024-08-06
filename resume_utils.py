# resume_utils.py

import os
import re
import csv
import spacy
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Regular expressions for phone and email extraction
PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
EMAIL_REG = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

def read_skills_from_csv(file_path):
    """Reads skills from a CSV file and returns them as a list."""
    skills = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row
            for row in reader:
                if row:
                    skills.append(row[0].strip())
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"Error reading the skills file: {e}")
    return skills

def extract_phone_number(text):
    """Extracts the first phone number found in the given text."""
    phone = re.findall(PHONE_REG, text)
    if phone:
        number = ''.join(phone[0])
        if text.find(number) >= 0 and len(number) < 16:
            return number
    return None

def extract_email(text):
    """Extracts all email addresses found in the given text."""
    emails = re.findall(EMAIL_REG, text)
    return emails if emails else None

def extract_skills(text, skills_list):
    """Extracts skills from the given text based on the provided skills list."""
    found_skills = []
    for skill in skills_list:
        if re.search(rf'\b{skill}\b', text, re.IGNORECASE):
            found_skills.append(skill)
    return found_skills

def parse_resume(filepath, skills_list):
    # Set up the parser
    parser = LlamaParse(result_type="markdown")
    _, file_extension = os.path.splitext(filepath)
    
    try:
        file_extractor = {file_extension: parser}
        documents = SimpleDirectoryReader(input_files=[filepath], file_extractor=file_extractor).load_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    
    if not documents:
        print("No documents found.")
        return None
    
    text = documents[0].text
    if text:
        phone_number = extract_phone_number(text)
        email_addresses = extract_email(text)
        skills = extract_skills(text, skills_list)
        
        return {
            "phone_number": phone_number,
            "email_addresses": email_addresses,
            "skills": skills
        }
    else:
        print("No text extracted from the document.")
        return None
