from langchain_community.document_loaders import PyPDFLoader
from langchain_classic.schema import Document
from app.guard_rails.pii_masking import PIIGuard
import os
from typing import List
guard = PIIGuard()


def load_pdf(file_path: str, user_id: str, role: str, access_details: List[str]):
   
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    masked_documents = []

    for i, doc in enumerate(documents, start=1):
       
        masked_text, detected = guard.mask(doc.page_content)

        if detected:
            print("Detected PII types:", list(detected.keys()))

       
        metadata = doc.metadata.copy() if doc.metadata else {}
        metadata.update({
            "user_id": user_id,
            "role": role,
            "page_number": i,
            "source": file_path,
            "filename": os.path.basename(file_path) ,
            "allowed_roles": access_details
        })

       
        masked_doc = Document(
            page_content=masked_text,
            metadata=metadata
        )

        masked_documents.append(masked_doc)
        print(f"Masked document {masked_documents}")
   
    return masked_documents