from app.ingestion.emb import get_embeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

load_dotenv()



def create_vector_store(chunks):
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise RuntimeError("PINECONE_API_KEY is not configured")

    pc = Pinecone(api_key=api_key)

    index_name = os.getenv("PINECONE_INDEX_NAME", "capstone-rag")

   
    existing_indexes = [i.name for i in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=384,  
            metric="cosine",
            spec=ServerlessSpec(
                cloud=os.getenv("PINECONE_CLOUD", "aws"),
                region=os.getenv("PINECONE_REGION", "us-east-1")
            )
        )

   
    index = pc.Index(index_name)

    
    vector_store = PineconeVectorStore(
        index=index,
        embedding=get_embeddings()
    )
    vector_store.add_documents(chunks)  
    
    return vector_store
