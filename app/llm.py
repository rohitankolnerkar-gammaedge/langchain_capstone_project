from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
import os


def get_llm():
        api_key = os.getenv("GROK_API_KEY")
        return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature = 0,
        api_key=api_key)