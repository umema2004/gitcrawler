# GitCrawler: GitHub Repository and Resume Matcher
This project is a Flask web application that matches skills listed in a resume with skills and languages used in a user's GitHub repositories. The application uses the GitHub API to fetch repository details and matches these with keywords extracted from a user's resume.

## Features
### Resume Upload: Upload a resume in plain text format.
### GitHub Integration: Fetch user repositories, languages used, and README content from GitHub.
### Skill Matching: Match skills from the resume with languages and keywords in repository README files.
### CSV Report: Generate and download a CSV report of matched skills and repository details.
### Flash Messages: Display feedback messages for successful uploads, downloads, and errors.

## Prerequisites
Python 3.x

Flask

NLTK (Natural Language Toolkit)

Bootstrap (for front-end styling)

## Usage
1. Run app.py
2. Open your web browser and go to http://127.0.0.1:5000/.
3. Enter your GitHub username and personal access token.
4. Upload your resume in plain text format.
5. Click on the "Upload" button.
6. After processing, view the results on the results page.
7. Download the generated CSV report if needed.
