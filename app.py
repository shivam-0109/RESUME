import gradio as gr
import os
import json
from parcv import parcv
import pandas as pd

# Initialize parser once
parser = parcv.Parser(pickle=True, load_pickled=True)

# Function to process folder of PDFs and extract structured data
def process_resume_folder(pdf_files):
    results = []

    for file in pdf_files:
        try:
            parsed_json = parser.parse(file.name)
            name = parsed_json.get("Name", "Unknown")
            contact = parsed_json.get("Contact Info", {})
            job_history = parsed_json.get("Job History", [])
            education = parsed_json.get("Education", [])
            skills = parsed_json.get("Skills", [])

            results.append({
                "File Name": os.path.basename(file.name),
                "Name": name,
                "Phone": contact.get("phone1", ""),
                "Email": contact.get("Email", ""),
                "Job History": "; ".join([f"{j.get('Job Title', '')} at {j.get('Company', '')} ({j.get('Start Date', '')} to {j.get('End Date', '')})" for j in job_history]),
                "Education": "; ".join(education),
                "Skills": ", ".join(skills)
            })

        except Exception as e:
            results.append({
                "File Name": os.path.basename(file.name),
                "Name": "Error parsing",
                "Phone": "-",
                "Email": "-",
                "Job History": "-",
                "Education": "-",
                "Skills": f"Error: {str(e)}"
            })

    df = pd.DataFrame(results)
    return df


# Gradio Interface
gr.Interface(
    fn=process_resume_folder,
    inputs=gr.File(file_types=[".pdf"], file_count="directory", label="Upload Folder of CVs (PDF format)"),
    outputs=gr.Dataframe(headers=["File Name", "Name", "Phone", "Email", "Job History", "Education", "Skills"], type="pandas"),
    title="Batch Resume Parser",
    description="Upload a folder of resumes (PDF) and extract structured details like Name, Contact, Job History, Education, and Skills."
).launch()
