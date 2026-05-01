from app.ingestion.emb import get_embeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

def get_retriever( role: str):
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise RuntimeError("PINECONE_API_KEY is not configured")

    pc = Pinecone(
        api_key=api_key
    )
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "capstone-rag"))

    
    vector_store = PineconeVectorStore(
        index=index,
        embedding=get_embeddings(),
        
    )
    retriever = vector_store.as_retriever(
        search_kwargs={
        "k": 3,
        "filter": {
            "allowed_roles": {"$in": [role]}
            }
        }
    )

    return retriever
