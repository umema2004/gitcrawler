import requests
import re
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

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

# Compile a List of Languages
def aggregate_languages(repos_languages):
    language_count = defaultdict(int)
    for repo_languages in repos_languages:
        for language, lines in repo_languages.items():
            language_count[language] += lines
    return language_count

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

# Main function
def main():
    username = input("Enter the GitHub username: ")
    token = "YOUR API KEY"
    file_path = input("Enter the path to the CV text file: ")
    
    # Read the CV text file and extract important words
    with open(file_path, 'r') as file:
        cv_text = file.read()
    items_from_cv = extract_important_words(cv_text)
    
    try:
        # Get repositories
        repos = get_user_repositories(username, token)
        
        # Get languages and README content for each repository
        languages = []
        repo_details = []
        all_items_found = set()
        for repo in repos:
            repo_languages = get_repo_languages(repo['full_name'], token)
            languages.append(repo_languages)
            repo_details.append((repo['name'], list(repo_languages.keys())))
            
            readme_content = get_repo_readme(repo['full_name'], token)
            items_found_in_readme = find_items_in_readme(readme_content, items_from_cv)
            all_items_found.update(items_found_in_readme)
            
            items_found_in_languages = find_items_in_languages(repo_languages, items_from_cv)
            all_items_found.update(items_found_in_languages)
        
        # Output results
        print(f"\nUsername: {username}")
        print(f"\nNumber of repositories: {len(repos)}")
        print("\nRepositories and their languages:")
        for repo_name, repo_languages in repo_details:
            print(f"- {repo_name}: {', '.join(repo_languages)}")
        print(f"\nMatched Items from CV in README and Languages: {', '.join(all_items_found)}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from GitHub API: {e}")

# Run the main function
if __name__ == "__main__":
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')
    main()
