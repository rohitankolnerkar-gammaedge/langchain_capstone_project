from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.llm import get_llm

def create_rag_chain(role: str = None):
    llm = get_llm()

    prompt = ChatPromptTemplate.from_template("""
Answer the question using ONLY the information in the context below.
If the answer cannot be found in the context, respond exactly with:

{{
  "answer": "Answer not in context",
  "sources": []
}}

Return valid JSON ONLY.
Chat History:
{chat_history}
                                              
Context:
{context}

Question:
{question}
""")

    rag_chain = (prompt
                 | llm
                 | StrOutputParser()
                 )

    return rag_chain