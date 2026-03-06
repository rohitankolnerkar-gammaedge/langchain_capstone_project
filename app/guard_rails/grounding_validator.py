from langchain_core.prompts import ChatPromptTemplate
from app.llm import get_llm
import json
import re


class GroundingValidator:

    def __init__(self):
        self.llm = get_llm()

        self.prompt = ChatPromptTemplate.from_template(
        """
You are a grounding validator.

Check whether the answer is supported by the context.

Rules:
- Paraphrasing is allowed.
- If the answer adds information not present in the context,
  it is NOT GROUNDED.

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
                "grounded": False,
                "reason": f"Invalid JSON from LLM: {content}"
            }

        return parsed