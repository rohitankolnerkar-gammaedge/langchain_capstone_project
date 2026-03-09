from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.llm import get_llm

def create_rag_chain(role: str = None):
    llm = get_llm()

    prompt = ChatPromptTemplate.from_template(
"""
You are a helpful assistant answering questions using company policy documents.

Rules:
- Answer ONLY using the provided context
- Provide a clear explanatory answer in full sentences.
- Do NOT give short answers like "10 days".
- Include important conditions or details from the policy.
- Provide a clear explanation
- Do not hallucinate
- If the answer is not found say "Not found in context"

Context:
{context}
Chat History:
{chat_history}

Question:
{question}

Return JSON:
{{
 "answer": "...",
 "sources": ["section"]
}}
"""
)

    rag_chain = (prompt
                 | llm
                 | StrOutputParser()
                 )

    return rag_chain