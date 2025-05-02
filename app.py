import streamlit as st
import pdfplumber
import re
import json
import spacy
from io import BytesIO

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Predefined skills list (expandable)
SKILLS_DB = [
    'Python', 'Java', 'SQL', 'Excel', 'Machine Learning', 'Deep Learning',
    'Tableau', 'Power BI', 'Data Analysis', 'TensorFlow', 'Keras',
    'Communication', 'Leadership', 'Teamwork', 'Problem Solving'
]

# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Extract basic info
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

# Extract skills using spaCy
def extract_skills(text):
    doc = nlp(text)
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    found_skills = set()

    for token in tokens:
        if token.lower() in map(str.lower, SKILLS_DB):
            found_skills.add(token)

    return list(found_skills)

# Extract work experience (basic version)
def extract_experience(text):
    experience = []
    exp_pattern = re.findall(r'(?i)([A-Z][\w\s&,.]+)\s*[\n\-:]+\s*(.+?)\s+(\w{3,9}\s+\d{4})\s*-\s*(\w{3,9}\s+\d{4}|Present)', text)
    
    for match in exp_pattern:
        company, role, start, end = match
        experience.append({
            "Company": company.strip(),
            "Job Title": role.strip(),
            "Duration": f"{start} - {end}",
            "Description": ""  # Optional: extract nearby lines
        })
    return experience

# Streamlit app
st.title("📄 Resume Parser App (NLP-Based)")
uploaded_file = st.file_uploader("Upload a PDF Resume", type="pdf")

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.subheader("Parsed Resume Information")

    parsed_data = extract_basic_info(text)
    parsed_data["Skills"] = extract_skills(text)
    parsed_data["Work Experience"] = extract_experience(text)
    parsed_data["Education"] = []  # Placeholder
    parsed_data["Certifications"] = []  # Placeholder
    parsed_data["Projects"] = []  # Placeholder

    st.json(parsed_data)

    json_data = json.dumps(parsed_data, indent=4)
    st.download_button("Download Extracted Data", json_data, file_name="parsed_resume.json", mime="application/json")
