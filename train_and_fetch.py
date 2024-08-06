# train_and_fetch.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
import joblib
import os
from github_utils import fetch_python_files  # Import the shared functions

# Load dataset for training the models
df = pd.read_csv('dataset.csv')
X = df['Source Code']
y_skill = df['Skill']
y_skill_level = df['Skill Level']

# Split into training and test sets
X_train, X_test, y_skill_train, y_skill_test = train_test_split(X, y_skill, test_size=0.2, random_state=42)
_, _, y_skill_level_train, y_skill_level_test = train_test_split(X, y_skill_level, test_size=0.2, random_state=42)

# Create and train the skill classification model
skill_model = make_pipeline(TfidfVectorizer(), MultinomialNB())
skill_model.fit(X_train, y_skill_train)

# Create and train the skill level classification model
skill_level_model = make_pipeline(TfidfVectorizer(), MultinomialNB())
skill_level_model.fit(X_train, y_skill_level_train)

# Save the models
joblib.dump(skill_model, 'skill_classifier2.pkl')
joblib.dump(skill_level_model, 'skill_level_classifier2.pkl')

# Fetch Python files from GitHub user repositories
username = 'umema2004'  # replace with the GitHub username
token = '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'  # replace with your GitHub token
python_files = fetch_python_files(username, token)

# Process the Python files to predict skills and skill levels
predicted_skills = skill_model.predict(python_files)
predicted_skill_levels = skill_level_model.predict(python_files)

# Aggregate results into a dictionary with highest skill level
skill_level_dict = {}
for skill, skill_level in zip(predicted_skills, predicted_skill_levels):
    if skill not in skill_level_dict or skill_level > skill_level_dict[skill]:
        skill_level_dict[skill] = skill_level

# Update skills CSV
skills_csv_path = 'skills.csv'

if os.path.exists(skills_csv_path):
    skills_df = pd.read_csv(skills_csv_path)
else:
    skills_df = pd.DataFrame(columns=['Skill'])

new_skills = pd.Series(predicted_skills).unique()
new_skills_df = pd.DataFrame({'Skill': new_skills})
skills_df = pd.concat([skills_df, new_skills_df]).drop_duplicates().reset_index(drop=True)

skills_df.to_csv(skills_csv_path, index=False)

# Print the skill level dictionary
print("Skill Levels Dictionary:")
for skill, level in skill_level_dict.items():
    print(f"{skill}: {level}")

print("Training complete and skills CSV updated.")
