from fastapi import UploadFile, File, Form, APIRouter, HTTPException
from typing import List
from dotenv import load_dotenv
import os
import zipfile
import shutil
from app.ingestion.pipeline import ingest_pdf

load_dotenv()

input_doc = APIRouter()

@input_doc.post("/input-document")
async def ask(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    role: str = Form(...),
    access_details: List[str]= Form(...)
):
    ALLOWED_TYPES = ["application/pdf", "application/zip"]

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF or ZIP files allowed")

  
    temp_dir = "temp_upload"
    os.makedirs(temp_dir, exist_ok=True)

    file_path = os.path.join(temp_dir, file.filename)

  
    with open(file_path, "wb") as f:
        f.write(await file.read())

    ingestion_results = []

   
    if file.content_type == "application/pdf":
        result = ingest_pdf(file_path, user_id=user_id, role=role,access_details=access_details)
        ingestion_results.append({file.filename: result})

  
    elif file.content_type == "application/zip":

        extract_path = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_path, exist_ok=True)

     
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

     
        for root, _, files in os.walk(extract_path):
            for filename in files:
                if filename.endswith(".pdf"):
                    pdf_path = os.path.join(root, filename)
                    result = ingest_pdf(pdf_path, user_id=user_id, role=role, access_details=access_details)
                    ingestion_results.append({filename: result})

        shutil.rmtree(extract_path)

   
    os.remove(file_path)

    return {
        "message": "File(s) ingested successfully",
        "details": ingestion_results
    }