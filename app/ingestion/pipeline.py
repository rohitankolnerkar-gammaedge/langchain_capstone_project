from app.ingestion.loader import load_pdf
from app.ingestion.spliter import split_documents
from app.ingestion.embedding import create_vector_store
import time
from app.monitoring.mertics import PDF_LOADING_LATENCY, PDF_SPLITTING_LATENCY, PDF_EMBEDDING_LATENCY, PDF_TOTAL_INGESTION_LATENCY
from typing import List
def ingest_pdf(file_path: str, user_id: str, role: str, access_details: List[str]):

    request_start = time.perf_counter()

    try:
        
        loading_start = time.perf_counter()
        documents = load_pdf(file_path, user_id=user_id, role=role, access_details=access_details)
        loading_latency = time.perf_counter() - loading_start
        PDF_LOADING_LATENCY.observe(loading_latency)
        print(f"Loading latency: {loading_latency * 1000:.2f} ms")

       
        splitting_start = time.perf_counter()
        chunks = split_documents(documents)
        splitting_latency = time.perf_counter() - splitting_start
        PDF_SPLITTING_LATENCY.observe(splitting_latency)
        print(f"Splitting latency: {splitting_latency * 1000:.2f} ms")

       
        embedding_start = time.perf_counter()
        vector_store = create_vector_store(chunks)
        embedding_latency = time.perf_counter() - embedding_start
        PDF_EMBEDDING_LATENCY.observe(embedding_latency)
        print(f"Embedding latency: {embedding_latency * 1000:.2f} ms")

        
        total_latency = time.perf_counter() - request_start
        PDF_TOTAL_INGESTION_LATENCY.observe(total_latency)
        print(f"Total ingestion latency: {total_latency * 1000:.2f} ms")

        return {
            "pages": len(documents),
            "chunks": len(chunks)
        }

    except Exception as e:
        raise e