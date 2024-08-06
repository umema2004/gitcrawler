# GIT-CRAWLER - GitHub Skills Predictor

This project is a web application that predicts skills and skill levels based on a user's GitHub repositories and uploaded resume. It uses machine learning models to analyze the source code in the repositories and the text in the resume to generate predictions. The results are presented to the user along with an option to download a CSV file containing the predicted skills and their levels.

## Features

- Upload a resume in PDF, DOC, or DOCX format.
- Provide a GitHub username to fetch and analyze repositories.
- Predict skills and skill levels based on the content of the resume and GitHub repositories.
- Display matched skills found in both the resume and GitHub repositories.
- Download the prediction results as a CSV file.

## Requirements

- Python 3.6+
- Flask
- Requests
- Pandas
- Scikit-learn
- Joblib
- Spacy
- LlamaParse

## Installation

1. Clone the repository:
    
    ``` sh
   git clone https://github.com/yourusername/github-skills-predictor.git
    cd github-skills-predictor
   ```
    

3. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

4. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

5. Download the spaCy model:
    ``` sh
    python -m spacy download en_core_web_sm
    ```

## Setup

1. Add your GitHub token in the app.py file:
    ``` python
    app.config['GITHUB_TOKEN'] = 'YOUR_GITHUB_TOKEN'
    ```

2. Ensure the directories for uploads and CSV outputs exist:
    ``` sh
    mkdir -p uploads csv_outputs
    ```

3. Ensure the trained models (skill_classifier2.pkl and skill_level_classifier2.pkl) are in the project directory.

## Usage

1. Start the Flask server:
    ``` sh
    python app.py
    ```

2. Open a web browser and navigate to http://127.0.0.1:5000.

3. Fill in the form with your GitHub username and upload your resume.

4. Click on the "Predict Skills" button.

5. View the predicted skills, skill levels, and matched skills.

6. Download the CSV file with the prediction results using the provided link.

## File Descriptions

- app.py: Main Flask application file that handles requests and serves the web interface.
- index2.html: HTML template for the web interface.
- requirements.txt: List of Python packages required for the project.
- github_utils.py: Contains functions to interact with the GitHub API.
- resume_utils.py: Contains functions to parse resumes and extract skills.
- uploads/: Directory for uploaded resume files.
- csv_outputs/: Directory for output CSV files.

## Contributing

1. Fork the repository.
2. Create a new branch: git checkout -b feature-branch.
3. Make your changes and commit them: git commit -m 'Add some feature'.
4. Push to the branch: git push origin feature-branch.
5. Open a pull request.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [spaCy](https://spacy.io/)
- [LlamaParse](https://github.com/yourusername/llamaparse)
- [GitHub API](https://docs.github.com/en/rest)

---

Umema Ashar 22i2036
Knowledge Data Dsicovery Lab FAST NUCES
