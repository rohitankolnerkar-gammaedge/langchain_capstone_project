from fpdf import FPDF
import zipfile
import os
import lorem
import random

# Subjects list (50 different subjects)
subjects = [
    "Mathematics", "Physics", "Chemistry", "Biology", "History", "Geography",
    "Computer Science", "Economics", "Psychology", "Sociology", "Philosophy",
    "Political Science", "Literature", "Art", "Music", "Engineering",
    "Medicine", "Astronomy", "Statistics", "Environmental Science", "Law",
    "Education", "Anthropology", "Linguistics", "Business Studies", "Finance",
    "Marketing", "Management", "Accounting", "Ethics", "Theology", "Geology",
    "Architecture", "Robotics", "AI", "Machine Learning", "Data Science",
    "Cybersecurity", "Networking", "Journalism", "Film Studies", "Theater",
    "Sports Science", "Nutrition", "Pharmacy", "Veterinary Science", "Astronautics",
    "Genetics", "Nanotechnology", "Renewable Energy", "Blockchain"
]

# Create folder for PDFs
os.makedirs("pdfs", exist_ok=True)

# Generate PDFs
for i, subject in enumerate(subjects, start=1):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Random number of pages between 5 and 10
    num_pages = random.randint(5, 10)
    
    for page in range(1, num_pages + 1):
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"{subject} - Page {page}", ln=True)
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        
        # Add 5–10 paragraphs of lorem text per page
        for _ in range(random.randint(5, 10)):
            paragraph = lorem.paragraph()
            pdf.multi_cell(0, 8, paragraph)
            pdf.ln(2)
    
    pdf_file = f"pdfs/{subject.replace(' ', '_')}.pdf"
    pdf.output(pdf_file)

# Zip all PDFs
with zipfile.ZipFile("all_subjects.zip", "w") as zipf:
    for file_name in os.listdir("pdfs"):
        zipf.write(os.path.join("pdfs", file_name), arcname=file_name)

print("ZIP file 'all_subjects.zip' created with 50 PDFs, each 5–10 pages long.")