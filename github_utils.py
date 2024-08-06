# github_utils.py

import requests
import base64

def get_user_repositories(username, token):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_repo_details(repo_full_name, token):
    url = f"https://api.github.com/repos/{repo_full_name}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_repo_files(repo_full_name, branch, token):
    url = f"https://api.github.com/repos/{repo_full_name}/git/trees/{branch}?recursive=1"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_file_content(repo_full_name, file_path, token):
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    content = response.json()
    return base64.b64decode(content['content']).decode('utf-8')

def fetch_python_files(username, token):
    repos = get_user_repositories(username, token)
    python_files = []
    for repo in repos:
        repo_full_name = repo['full_name']
        repo_details = get_repo_details(repo_full_name, token)
        default_branch = repo_details['default_branch']
        try:
            repo_files = get_repo_files(repo_full_name, default_branch, token)
            for file in repo_files['tree']:
                if file['path'].endswith('.py'):
                    content = get_file_content(repo_full_name, file['path'], token)
                    python_files.append(content)
        except requests.exceptions.HTTPError as e:
            print(f"Error fetching files for repo {repo_full_name}: {e}")
    return python_files
