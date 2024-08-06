# app.py

from flask import Flask, request, render_template, jsonify, send_file
import joblib
import os
from werkzeug.utils import secure_filename
import pandas as pd
from github_utils import fetch_python_files  # Import the shared functions
from resume_utils import parse_resume, read_skills_from_csv  # Import resume parsing functions

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CSV_FOLDER'] = 'csv_outputs'
app.config['GITHUB_TOKEN'] = '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'  # Add your GitHub token here

# Load the trained models
skill_model = joblib.load('skill_classifier.pkl')
skill_level_model = joblib.load('skill_level_classifier.pkl')

# Path to the skills CSV file
skills_csv_path = 'skills.csv'

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/predict', methods=['POST'])
def predict():
    github_username = request.form['github_username']
    resume = request.files['resume']

    # Save resume file
    filename = secure_filename(resume.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    resume.save(file_path)

    # Read skills from CSV
    skills_list = read_skills_from_csv(skills_csv_path)

    # Parse resume
    resume_details = parse_resume(file_path, skills_list)
    resume_skills = resume_details['skills'] if resume_details else []

    # Remove the saved file after parsing
    os.remove(file_path)

    # Fetch Python files from GitHub
    python_files = fetch_python_files(github_username, app.config['GITHUB_TOKEN'])
    predicted_skills = skill_model.predict(python_files)
    predicted_skill_levels = skill_level_model.predict(python_files)

    # Aggregate results into a dictionary with highest skill level
    skill_level_dict = {}
    for skill, skill_level in zip(predicted_skills, predicted_skill_levels):
        if skill not in skill_level_dict or skill_level > skill_level_dict[skill]:
            skill_level_dict[skill] = skill_level

    # Determine matched skills
    matched_skills = set(resume_skills).intersection(skill_level_dict.keys())

    # Combine resume details and GitHub skill predictions
    result = {
        "GitHub Skills": skill_level_dict,
        "Resume Details": resume_details,
        "Matched Skills": list(matched_skills)
    }

    # Create a DataFrame for the results
    results_df = pd.DataFrame({
        'Skill': list(skill_level_dict.keys()),
        'Skill Level': list(skill_level_dict.values())
    })

    # Save the results to a CSV file
    csv_filename = f"{github_username}_skills.csv"
    csv_filepath = os.path.join(app.config['CSV_FOLDER'], csv_filename)
    results_df.to_csv(csv_filepath, index=False)

    # Return JSON response with download link
    result['csv_download_link'] = f'/download/{csv_filename}'
    return jsonify(result)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['CSV_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['CSV_FOLDER']):
        os.makedirs(app.config['CSV_FOLDER'])
    app.run(debug=True)
