# GIT-CRAWLER: GitHub Repository Analyzer

This script analyzes a GitHub user's repositories to find matches with skills, languages, project names, libraries, frameworks, and other items listed in a provided CV text file. It searches through the repository languages and README files to identify relevant matches.

## Features

- Fetches user repositories from GitHub.
- Extracts languages used in each repository.
- Analyzes README files for each repository.
- Identifies important words from a provided CV text file.
- Finds matches between CV items and repository details (languages and README content).
- Outputs a summary of matched items and repository details.

## Prerequisites

- Python 3.x
- `requests` library
- `nltk` library
- GitHub Personal Access Token

## Installation

1. Clone the repository:

```bash
git clone https://github.com/umema2004/gitcrawler.git
cd gitcrawler

2. Install the required libraries:

pip install requests nltk

3. Download NLTK data:

import nltk
nltk.download('punkt')
nltk.download('stopwords')

## Usage

Run the script

python git-crawler.py

Run for given example file 'resume.txt'

## Example

Enter the GitHub username: umema2004
Enter the path to the CV text file: resume.txt
