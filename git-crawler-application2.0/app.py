from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
import os
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import csv

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'  # Necessary for flash messages
nltk.download('punkt')
nltk.download('stopwords')

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Fetch User Repositories
def get_user_repositories(username, token):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad responses
    return response.json()

# Fetch Languages for Each Repository
def get_repo_languages(repo_full_name, token):
    url = f"https://api.github.com/repos/{repo_full_name}/languages"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad responses
    return response.json()

# Fetch README content for Each Repository
def get_repo_readme(repo_full_name, token):
    url = f"https://api.github.com/repos/{repo_full_name}/readme"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3.raw"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text.lower()  # Convert to lowercase
    else:
        return ""

# Find items in README content
def find_items_in_readme(readme_content, items_list):
    found_items = set()
    for item in items_list:
        if item.lower() in readme_content:
            found_items.add(item)
    return found_items

# Find items in repository languages
def find_items_in_languages(repo_languages, items_list):
    found_items = set()
    for item in items_list:
        if item.lower() in repo_languages:
            found_items.add(item)
    return found_items

# Extract important words from the text file
def extract_important_words(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    important_words = [word for word in word_tokens if word.isalnum() and word.lower() not in stop_words]
    return set(important_words)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        username = request.form['username']
        token = request.form['token']
        file = request.files['file']
        if file and username and token:
            if not file.filename.endswith('.txt'):
                flash('Only text files are allowed!', 'error')
                return redirect(request.url)
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            return redirect(url_for('process_file', username=username, token=token, filename=filename))
        else:
            flash('All fields are required!', 'error')
            return redirect(request.url)
    return render_template('upload.html')

@app.route('/process', methods=['GET'])
def process_file():
    username = request.args.get('username')
    token = request.args.get('token')
    filename = request.args.get('filename')

    with open(filename, 'r') as file:
        cv_text = file.read()
    items_from_cv = extract_important_words(cv_text)

    try:
        repos = get_user_repositories(username, token)

        languages = []
        repo_details = []
        all_items_found = set()
        repo_skills = []

        for repo in repos:
            repo_languages = get_repo_languages(repo['full_name'], token)
            languages.append(repo_languages)
            repo_details.append((repo['name'], list(repo_languages.keys())))

            readme_content = get_repo_readme(repo['full_name'], token)
            items_found_in_readme = find_items_in_readme(readme_content, items_from_cv)
            items_found_in_languages = find_items_in_languages(repo_languages, items_from_cv)

            items_found = items_found_in_readme.union(items_found_in_languages)
            repo_skills.append((repo['name'], items_found))
            all_items_found.update(items_found)

        output_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{username}.csv")
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Username", username])
            writer.writerow(["Number of repositories", len(repos)])
            writer.writerow(["\n"])
            writer.writerow(["Repository", "Languages"])
            for repo_name, repo_languages in repo_details:
                writer.writerow([repo_name, ', '.join(repo_languages)])
            writer.writerow(["\n"])
            writer.writerow(["Matched Items from CV in README and Languages"])
            writer.writerow([', '.join(all_items_found)])
            writer.writerow(["\n"])
            writer.writerow(["Skills found in each repository"])
            writer.writerow(["Repository", "Skills"])
            for repo_name, skills in repo_skills:
                writer.writerow([repo_name, ', '.join(skills)])

        flash('Processing complete!', 'success')
        return render_template('results.html', username=username, repos=repo_details, skills=repo_skills, output_file=url_for('download_file', filename=f"{username}.csv"))

    except requests.exceptions.RequestException as e:
        flash(f"Error fetching data from GitHub API: {e}", 'error')
        return redirect(url_for('upload_file'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
