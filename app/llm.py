from langchain_groq import ChatGroq

from dotenv import load_dotenv

import os

load_dotenv()


def get_llm():
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        temperature=0,
        api_key=api_key
    )
