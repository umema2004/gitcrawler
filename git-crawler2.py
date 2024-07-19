import requests
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import csv
import fitz
import nltk
import base64
import json
import re
nltk.download('punkt')
nltk.download('stopwords')

# username = 'umema2004'
username=input("Enter username: ")
token = "ENTER YOUR TOKEN"
# file_path = 'resume.txt'
file_path=input("Enter Cv file path: ")
output_file = username + ".csv"

def read_text_from_file(file_path):
    if file_path.lower().endswith('.txt'):
        with open(file_path, 'r') as file:
            return file.read()
    elif file_path.lower().endswith('.pdf'):
        try:
            pdf_document = fitz.open(file_path)
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Failed to open PDF file '{file_path}': {e}")
            raise
    else:
        raise ValueError("Unsupported file format. Please provide a .txt or .pdf file.")
    
def extract_important_words(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    important_words = [word for word in word_tokens if word.isalnum() and word.lower() not in stop_words]
    return set(important_words)

def get_user_repositories(username, token):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad responses
    return response.json()

def get_repo_languages(repo_full_name, token):
    url = f"https://api.github.com/repos/{repo_full_name}/languages"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad responses
    return response.json()

def get_repo_files(repo_full_name, token):
    url = f"https://api.github.com/repos/{repo_full_name}/git/trees/main?recursive=1"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad responses
    return response.json()

def get_file_content(repo_full_name, file_path, token):
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad responses
    
    file_content = response.json()
    
    if file_content.get('encoding') == 'base64':
        # Decode the base64 content
        return base64.b64decode(file_content['content']).decode('utf-8')
    else:
        return file_content['content']

def preprocess_source_code(content, file_extension):
    if file_extension == '.py':
        # Remove Python comments and strip whitespace
        content = re.sub(r'#.*', '', content)
    elif file_extension == '.js':
        # Remove JavaScript comments and strip whitespace
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    elif file_extension == '.ipynb':
        # Parse JSON content of the Jupyter Notebook
        notebook = json.loads(content)
        
        # Iterate over all cells and preprocess code cells
        for cell in notebook.get('cells', []):
            if cell['cell_type'] == 'code':
                # Join the lines of code, remove comments, and strip whitespace
                cell_content = '\n'.join(cell['source'])
                cell_content = re.sub(r'#.*', '', cell_content)
                cell['source'] = [line.strip() for line in cell_content.split('\n') if line.strip()]
        
        # Convert notebook object back to JSON string
        content = json.dumps(notebook, indent=2)
    elif file_extension == '.html':
        # Remove HTML comments and strip whitespace
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        content = content.strip()
    elif file_extension == '.css':
        # Remove CSS comments and strip whitespace
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = content.strip()
    elif file_extension == '.js' or file_extension == '.cpp':
        # Remove JavaScript comments (both single-line and multi-line) and strip whitespace
        content = re.sub(r'//.*', '', content)  # Single-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)  # Multi-line comments
        content = content.strip()
    # Normalize line endings and strip leading/trailing whitespace
    content = '\n'.join([line.strip() for line in content.splitlines()])
    return content

def get_all_source_code(repo_full_name, token):
    repo_files = get_repo_files(repo_full_name, token)
    source_code_files = {}
    
    for file in repo_files['tree']:
        if file['type'] == 'blob' and file['path'].endswith(('.py','ipynb', '.js', '.java', '.cpp', '.c', '.rb', '.go', '.rs', '.php', '.html', '.css')):  # Add or modify extensions as needed
            file_pathmeow = file['path']
            file_content = get_file_content(repo_full_name, file_pathmeow, token)
            preprocessed_content = preprocess_source_code(file_content, file_pathmeow[file_pathmeow.rfind('.'):])
            source_code_files[file_pathmeow] = preprocessed_content
    
    return source_code_files

repos = get_user_repositories(username, token)
full_names = [repo["full_name"] for repo in repos]

all_repos_source_code={}

for repo_full_name in full_names:
    languages = get_repo_languages(repo_full_name, token)
    if not languages:
        print(f"Skipping empty repository: {repo_full_name}")
        continue
    
    all_repos_source_code[repo_full_name] = get_all_source_code(repo_full_name, token)

repo_details = []
langs=[]

for repo in repos:
    repo_languages = get_repo_languages(repo['full_name'], token)
    langs.append(repo_languages)
    repo_details.append((repo['name'], list(repo_languages.keys())))

cv_text = read_text_from_file(file_path)
items = extract_important_words(cv_text)
items = {skill.lower() for skill in items}
items=list(items)

skills_found=[]
skills_level={}

for repo in repo_details:
    repo_name, languages = repo
    for language in languages:
        file_path="languages - " + language.lower() + ".csv"
        
        try:
            with open(file_path, mode='r', newline='') as csvfile:
                
                csvreader = csv.DictReader(csvfile)
                for row in csvreader:
                    
                    if row['skill'] in items:       #checking if skill is in CV
                        meow = username + '/' + repo_name
                        
                        for meow2 in all_repos_source_code[meow]:
                                
                                meow_list = row['beginner'].split(',')
                                
                                if row['beginner'] in all_repos_source_code[meow][meow2]:  #checking if identification in CSV
                                    if row['skill'] not in skills_found:
                                       skills_found.append(row['skill']) 
                                    
                                    meow_list = row['advanced'].split(',')
                                    for meow3 in meow_list:
                                        if meow3 in all_repos_source_code[meow][meow2]:
                                            skills_level[row['skill']]='advanced'
                                        
                                        else:
                                            meow_list = row['inter'].split(',')
                                            for meow4 in meow_list:
                                                if meow4 in all_repos_source_code[meow][meow2]:
                                                    skills_level[row['skill']]='intermediate'

                                                else:
                                                    skills_level[row['skill']]='beginner'

        except FileNotFoundError:
            # Handle the case where the file is not found
            print(f"File not found: {file_path}")

print(skills_level)

