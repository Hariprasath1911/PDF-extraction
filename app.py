import streamlit as st
import pdfplumber
import re
import json
import spacy
import subprocess
import importlib.util

# Automatically download the spaCy model if not present
model_name = "en_core_web_sm"

def is_model_installed(model_name):
    return importlib.util.find_spec(model_name) is not None

if not is_model_installed(model_name):
    st.warning("Downloading spaCy model...")
    subprocess.run(["python", "-m", "spacy", "download", model_name])

nlp = spacy.load(model_name)

# Predefined skills list
SKILLS_DB = [
    'Python', 'Java', 'SQL', 'Excel', 'Machine Learning', 'Deep Learning',
    'Tableau', 'Power BI', 'Data Analysis', 'TensorFlow', 'Keras',
    'Communication', 'Leadership', 'Teamwork', 'Problem Solving'
]

def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_basic_info(text):
    email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone = re.search(r'\+?\d[\d\s\-\(\)]{9,}\d', text)
    linkedin = re.search(r'https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9\-_/]+', text)
    name = text.strip().split('\n')[0] if text else "Not found"

    return {
        "Full Name": name,
        "Email": email.group(0) if email else "Not found",
        "Phone": phone.group(0) if phone else "Not found",
        "LinkedIn": linkedin.group(0) if linkedin else "Not found"
    }

def extract_skills(text):
    doc = nlp(text)
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    found_skills = set()
    for token in tokens:
        if token.lower() in map(str.lower, SKILLS_DB):
            found_skills.add(token)
    return list(found_skills)

def extract_experience(text):
    experience = []
    exp_pattern = re.findall(r'(?i)([A-Z][\w\s&,.]+)\s*[\n\-:]+\s*(.+?)\s+(\w{3,9}\s+\d{4})\s*-\s*(\w{3,9}\s+\d{4}|Present)', text)
    for match in exp_pattern:
        company, role, start, end = match
        experience.append({
            "Company": company.strip(),
            "Job Title": role.strip(),
            "Duration": f"{start} - {end}",
            "Description": ""
        })
    return experience

# Streamlit UI
st.title("📄 Resume Parser App (NLP-Based)")
uploaded_file = st.file_uploader("Upload a PDF Resume", type="pdf")

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.subheader("Parsed Resume Information")

    parsed_data = extract_basic_info(text)
    parsed_data["Skills"] = extract_skills(text)
    parsed_data["Work Experience"] = extract_experience(text)
    parsed_data["Education"] = []
    parsed_data["Certifications"] = []
    parsed_data["Projects"] = []

    st.json(parsed_data)

    json_data = json.dumps(parsed_data, indent=4)
    st.download_button("Download Extracted Data", json_data, file_name="parsed_resume.json", mime="application/json")
