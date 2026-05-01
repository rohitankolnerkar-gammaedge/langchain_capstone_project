from fastapi import UploadFile, File, Form, APIRouter, HTTPException
from typing import List
from dotenv import load_dotenv
import os
import zipfile
import tempfile
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

    if not user_id.strip() or not role.strip():
        raise HTTPException(status_code=400, detail="user_id and role are required")

    access_details = normalize_access_details(access_details)
    if not access_details:
        raise HTTPException(status_code=400, detail="At least one access detail is required")

    upload_root = "temp_upload"
    os.makedirs(upload_root, exist_ok=True)

    try:
        with tempfile.TemporaryDirectory(dir=upload_root) as temp_dir:
            safe_name = os.path.basename(file.filename or "upload")
            file_path = os.path.join(temp_dir, safe_name)

            with open(file_path, "wb") as f:
                f.write(await file.read())

            ingestion_results = []

            if file.content_type == "application/pdf":
                result = ingest_pdf(file_path, user_id=user_id, role=role, access_details=access_details)
                ingestion_results.append({safe_name: result})

            elif file.content_type == "application/zip":
                extract_path = os.path.join(temp_dir, "extracted")
                os.makedirs(extract_path, exist_ok=True)

                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    safe_extract(zip_ref, extract_path)

                for root, _, files in os.walk(extract_path):
                    for filename in files:
                        if filename.lower().endswith(".pdf"):
                            pdf_path = os.path.join(root, filename)
                            result = ingest_pdf(pdf_path, user_id=user_id, role=role, access_details=access_details)
                            ingestion_results.append({filename: result})

                if not ingestion_results:
                    raise HTTPException(status_code=400, detail="ZIP file did not contain any PDFs")
    except zipfile.BadZipFile as exc:
        raise HTTPException(status_code=400, detail="Invalid ZIP file") from exc

    return {
        "message": "File(s) ingested successfully",
        "details": ingestion_results
    }


def normalize_access_details(access_details: List[str]) -> List[str]:
    normalized = []
    for item in access_details:
        normalized.extend(part.strip() for part in item.split(",") if part.strip())
    return normalized


def safe_extract(zip_ref: zipfile.ZipFile, extract_path: str):
    root = os.path.abspath(extract_path)
    for member in zip_ref.infolist():
        destination = os.path.abspath(os.path.join(extract_path, member.filename))
        if not destination.startswith(root + os.sep) and destination != root:
            raise HTTPException(status_code=400, detail="ZIP file contains unsafe paths")
    zip_ref.extractall(extract_path)
