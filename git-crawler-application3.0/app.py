from flask import Flask, request, render_template, redirect, url_for, jsonify, send_file
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
import os
import io

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
    response.raise_for_status()
    return response.json()

def get_repo_languages(repo_full_name, token):
    url = f"https://api.github.com/repos/{repo_full_name}/languages"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_repo_files(repo_full_name, token):
    url = f"https://api.github.com/repos/{repo_full_name}/git/trees/main?recursive=1"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_file_content(repo_full_name, file_path, token):
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    file_content = response.json()
    if file_content.get('encoding') == 'base64':
        return base64.b64decode(file_content['content']).decode('utf-8')
    else:
        return file_content['content']

def preprocess_source_code(content, file_extension):
    if file_extension == '.py':
        content = re.sub(r'#.*', '', content)
    elif file_extension == '.js':
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    elif file_extension == '.ipynb':
        notebook = json.loads(content)
        for cell in notebook.get('cells', []):
            if cell['cell_type'] == 'code':
                cell_content = '\n'.join(cell['source'])
                cell_content = re.sub(r'#.*', '', cell_content)
                cell['source'] = [line.strip() for line in cell_content.split('\n') if line.strip()]
        content = json.dumps(notebook, indent=2)
    elif file_extension == '.html':
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        content = content.strip()
    elif file_extension == '.css':
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = content.strip()
    elif file_extension == '.cpp':
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = content.strip()
    content = '\n'.join([line.strip() for line in content.splitlines()])
    return content

def get_all_source_code(repo_full_name, token):
    repo_files = get_repo_files(repo_full_name, token)
    source_code_files = {}
    for file in repo_files['tree']:
        if file['type'] == 'blob' and file['path'].endswith(('.py', '.ipynb', '.js', '.java', '.cpp', '.c', '.rb', '.go', '.rs', '.php', '.html', '.css')):
            file_path = file['path']
            file_content = get_file_content(repo_full_name, file_path, token)
            preprocessed_content = preprocess_source_code(file_content, file_path[file_path.rfind('.'):])
            source_code_files[file_path] = preprocessed_content
    return source_code_files

def analyze_skills(username, token, file_path):
    repos = get_user_repositories(username, token)
    full_names = [repo["full_name"] for repo in repos]
    all_repos_source_code = {}

    for repo_full_name in full_names:
        languages = get_repo_languages(repo_full_name, token)
        if not languages:
            continue
        all_repos_source_code[repo_full_name] = get_all_source_code(repo_full_name, token)

    repo_details = []
    langs = []

    for repo in repos:
        repo_languages = get_repo_languages(repo['full_name'], token)
        langs.append(repo_languages)
        repo_details.append((repo['name'], list(repo_languages.keys())))

    cv_text = read_text_from_file(file_path)
    items = extract_important_words(cv_text)
    items = {skill.lower() for skill in items}
    items = list(items)

    skills_found_in_repos = {}
    skills_level = {}

    for repo in repo_details:
        repo_name, languages = repo
        repo_full_name = username + '/' + repo_name
        skills_found_in_repos[repo_name] = []

        for language in languages:
            language_file_path = "languages - " + language.lower() + ".csv"

            try:
                with open(language_file_path, mode='r', newline='') as csvfile:
                    csvreader = csv.DictReader(csvfile)
                    for row in csvreader:
                        if row['skill'] in items:
                            for file_path in all_repos_source_code[repo_full_name]:
                                if row['beginner'] in all_repos_source_code[repo_full_name][file_path]:
                                    if row['skill'] not in skills_found_in_repos[repo_name]:
                                        skills_found_in_repos[repo_name].append(row['skill'])
                                    if any(level in all_repos_source_code[repo_full_name][file_path] for level in row['advanced'].split(',')):
                                        skills_level[row['skill']] = 'advanced'
                                    elif any(level in all_repos_source_code[repo_full_name][file_path] for level in row['inter'].split(',')):
                                        skills_level[row['skill']] = 'intermediate'
                                    else:
                                        skills_level[row['skill']] = 'beginner'
            except FileNotFoundError:
                print(f"File not found: {language_file_path}")

    return skills_found_in_repos, skills_level

def save_skills_to_csv(skills_found_in_repos, skills_level, filename):
    with open(filename, mode='w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Repository', 'Skill', 'Level'])
        for repo, skills in skills_found_in_repos.items():
            for skill in skills:
                csvwriter.writerow([repo, skill, skills_level[skill]])


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        token = request.form['token']
        cv_file = request.files['cv_file']
        if cv_file:
            cv_file_path = os.path.join(app.config['UPLOAD_FOLDER'], cv_file.filename)
            cv_file.save(cv_file_path)
            skills_found_in_repos, skills_level = analyze_skills(username, token, cv_file_path)
            csv_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'skills_analysis.csv')
            save_skills_to_csv(skills_found_in_repos, skills_level, csv_filename)
            return redirect(url_for('results', skills_found_in_repos=json.dumps(skills_found_in_repos), skills_level=json.dumps(skills_level)))
    return render_template('index.html')

@app.route('/results')
def results():
    skills_found_in_repos = json.loads(request.args.get('skills_found_in_repos'))
    skills_level = json.loads(request.args.get('skills_level'))
    csv_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'skills_analysis.csv')
    return render_template('results.html', skills_found_in_repos=skills_found_in_repos, skills_level=skills_level, csv_filename=csv_filename)

@app.route('/download_csv')
def download_csv():
    csv_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'skills_analysis.csv')
    return send_file(csv_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
