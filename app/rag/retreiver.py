from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

def get_retriever( role: str):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    pc = Pinecone(
        api_key=os.getenv("PINECONE_API_KEY")
    )
    index = pc.Index("capstone-rag")

    
    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        
    )
    print(vector_store.index.describe_index_stats())
    retriever = vector_store.as_retriever(
        search_kwargs={
        "k": 5,
        "filter": {
            "allowed_roles": {"$in": [role]}
            }
        }
    )

    return retriever