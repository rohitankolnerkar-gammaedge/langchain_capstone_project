from langchain_community.embeddings import HuggingFaceEmbeddings
from functools import lru_cache
import os


@lru_cache(maxsize=1)
def get_embeddings():
    model_name = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    return HuggingFaceEmbeddings(model_name=model_name)
