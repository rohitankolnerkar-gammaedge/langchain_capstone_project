from langchain_core.prompts import ChatPromptTemplate
from app.llm import get_llm
import json
import re


class GroundingValidator:

    def __init__(self):
        self.llm = get_llm()

        self.prompt = ChatPromptTemplate.from_template(
        """
You are a grounding validator for a RAG system.

Determine whether the answer is supported by the context.

Guidelines:
- Paraphrasing of the context is allowed.
- Summarization of context is allowed.
- Minor general knowledge that does not contradict the context is allowed.
- Logical inference from the context is allowed.

Mark the answer as NOT grounded only if:
- The answer clearly contradicts the context
- The answer introduces major facts not present in the context
- The answer fabricates sources or claims unsupported information

Return JSON ONLY:

{{
  "grounded": true or false,
  "reason": "short explanation"
}}

Context:
{context}

Answer:
{answer}
"""
        )

        self.chain = self.prompt | self.llm

    async def validate(self, context: str, answer: str):

        result = await self.chain.ainvoke({
            "context": context,
            "answer": answer
        })

        content = result.content.strip()

        content = re.sub(r"```json|```", "", content).strip()

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {
                "grounded": True,  
                "reason": "Validator returned non-JSON response"
            }

        return parsed