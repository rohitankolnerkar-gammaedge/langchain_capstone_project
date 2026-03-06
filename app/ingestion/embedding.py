from app.ingestion.emb import embeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

load_dotenv()



def create_vector_store(chunks):
 
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    index_name = "capstone-rag"

   
    existing_indexes = [i.name for i in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=384,  
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"  
            )
        )

   
    index = pc.Index(index_name)

    
    vector_store = PineconeVectorStore(
    index=index,
    embedding=embeddings)
    vector_store.add_documents(chunks)  
    
    return vector_store