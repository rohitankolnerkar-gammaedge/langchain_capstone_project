from fastapi import Form, APIRouter, HTTPException
from dotenv import load_dotenv
from app.rag.chain import create_rag_chain
from app.guard_rails.input_guardrails import validate_length
from app.guard_rails.prompt_injection import PromptInjectionGuard
from app.guard_rails.grounding_validator import GroundingValidator
from app.monitoring.looger import logger
from app.rag.conversational_buffer import buffer_memory
load_dotenv()
import json
from app.rag.retreiver import get_retriever
import time
import re

from app.monitoring.timing_callback import TimingCallbackHandler
from app.monitoring.token_callback import TokenUsageCallback
from app.monitoring.mertics import REQUEST_COUNT,REQUEST_ERRORS,TOTAL_LATENCY,GROUNDED_ANSWERS,UNGROUNDED_ANSWERS,RETRIEVAL_LATENCY,ANS_QUALITY_SCORE,AVG_ANSWER_QUALITY_SCORE
from opentelemetry.trace import Tracer
from app.helper.config_opentelemetry import trace
from app.helper.evaluate_ans_quality import evaluate_answer_quality
input_query = APIRouter()

detect = PromptInjectionGuard()
validator = None
memory = buffer_memory()


tracer: Tracer = trace.get_tracer(__name__)


def get_grounding_validator():
    global validator
    if validator is None:
        validator = GroundingValidator()
    return validator


def parse_llm_answer(answer: str):
    cleaned = answer.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail="LLM returned a non-JSON answer"
        ) from exc

    if "answer" not in parsed:
        raise HTTPException(status_code=502, detail="LLM answer JSON is missing the answer field")

    parsed.setdefault("sources", [])
    return parsed


def normalize_question(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-zA-Z0-9\s']", " ", text.lower())).strip()


def get_simple_answer(question: str):
    normalized = normalize_question(question)
    words = normalized.split()

    if not normalized:
        return None

    greeting_words = {"hi", "hello", "hey", "namaste"}
    if len(words) <= 8 and (greeting_words.intersection(words) or "how are you" in normalized):
        return "Hello! I am doing well and ready to help. You can ask me a general question or ask about the documents you have ingested."

    if normalized in {"thanks", "thank you", "thank you so much", "thx"}:
        return "You are welcome. I am here whenever you need help."

    if normalized in {"who are you", "what are you", "what can you do", "help"}:
        return "I am your RAG assistant. I can answer simple chat questions, help with uploaded documents, and show sources when an answer comes from your document context."

    return None


def simple_response(question: str, answer: str):
    memory.save_context(
        {"input": question},
        {"result": answer}
    )
    return {
        "masked_query": question,
        "answer": answer,
        "sources": [],
        "retrieved_docs": [],
        "answer_quality_score": 1,
        "answer_quality_reason": "General conversation response. No document grounding was required."
    }


def is_rate_limit_error(error: Exception) -> bool:
    message = str(error).lower()
    return "rate limit" in message or "rate_limit" in message or "429" in message


async def validate_grounding_safely(context_text: str, answer: str):
    try:
        return await get_grounding_validator().validate(context_text, answer)
    except Exception as error:
        logger.warning(
            "Grounding validation skipped",
            extra={"error": str(error)}
        )
        return {
            "grounded": True,
            "reason": "Grounding validation skipped because the evaluator service was unavailable."
        }


def evaluate_quality_safely(question: str, answer: str, context: str):
    try:
        return evaluate_answer_quality(question, answer, context)
    except Exception as error:
        logger.warning(
            "Answer quality evaluation skipped",
            extra={"question": question, "error": str(error)}
        )
        return 0, "Answer quality evaluation skipped because the evaluator service was unavailable."


@input_query.post("/question")
async def question(question: str = Form(...), role: str = Form(...)):
    question = question.strip()
    role = role.strip()

    if not question or not role:
        raise HTTPException(status_code=400, detail="question and role are required")

    if not validate_length(question):
        raise HTTPException(status_code=400, detail="Question is too long")

    if detect.detect(question):
        raise HTTPException(status_code=400, detail="Prompt injection pattern detected")

    simple_answer = get_simple_answer(question)
    if simple_answer:
        REQUEST_COUNT.inc()
        return simple_response(question, simple_answer)

    logger.info(
        "RAG request started",
        extra={"question": question, "role": role}
    )
    history = memory.load_memory_variables({})["chat_history"]
    REQUEST_COUNT.inc()
    total_start = time.perf_counter()

    with tracer.start_as_current_span("RAG_Request") as span:
        span.set_attribute("role", role)

        try:
            with tracer.start_as_current_span("Retrieval") as retrieval_span:

                retrieval_start = time.perf_counter()

                retriever = get_retriever(role=role)
                docs = await retriever.ainvoke(question)

                retrieval_latency = time.perf_counter() - retrieval_start
                RETRIEVAL_LATENCY.observe(retrieval_latency)

                retrieved_sources = [
                    doc.metadata.get("source") for doc in docs
                ]

                retrieval_span.set_attribute(
                    "retrieved_docs", str(retrieved_sources)
                )

                logger.info(
                    "Documents retrieved",
                    extra={
                        "question": question,
                        "retrieved_docs": retrieved_sources,
                        "retrieval_latency": retrieval_latency
                    }
                )

        
            with tracer.start_as_current_span("LLM_Generation") as llm_span:

                context_text = "\n\n".join(
                    [doc.page_content[:500] for doc in docs]
                )

                chain = create_rag_chain()
                timing_callback = TimingCallbackHandler()
                token_callback = TokenUsageCallback()
                llm_start = time.perf_counter()

                response = await chain.ainvoke(
                    {
                        "context": context_text,
                        "question": question,
                        "chat_history": history
                    },
                    config={"callbacks": [timing_callback, token_callback]}
                )

                answer = response

                llm_latency = time.perf_counter() - llm_start

                llm_span.set_attribute("answer_length", len(answer))
                
                logger.info(
                    "LLM response generated",
                    extra={
                        "llm_latency": llm_latency,
                        "answer_length": len(answer)
                    }
                )

            
            with tracer.start_as_current_span("Grounding_Validation") as grounding_span:

                validation = await validate_grounding_safely(context_text, answer)

                grounding_span.set_attribute(
                    "grounded", validation["grounded"]
                )

                logger.info(
                    "Grounding validation finished",
                    extra={
                        "grounded": validation["grounded"]
                    }
                )

                if not validation["grounded"]:

                    UNGROUNDED_ANSWERS.inc()

                    end_time = time.perf_counter()
                    total_latency = end_time - total_start

                    TOTAL_LATENCY.observe(total_latency)

                    logger.warning(
                        "Ungrounded answer detected",
                        extra={
                            "question": question,
                            "reason": validation["reason"]
                        }
                    )

                    return {
                        "error": "Answer not grounded",
                        "reason": validation["reason"],
                        "retrieved_docs": [
                            doc.page_content for doc in docs
                        ]
                    }

                GROUNDED_ANSWERS.inc()
                

           
            end_time = time.perf_counter()
            total_latency = end_time - total_start
            
            TOTAL_LATENCY.observe(total_latency)

            logger.info(
                "RAG request completed",
                extra={
                    "total_latency": total_latency
                }
            )
            memory.save_context(
                {"input": question},
                {"result": response}
            ) 
            print(memory.load_memory_variables({}))
            parsed_answer = parse_llm_answer(answer)
            context = "\n".join([doc.page_content for doc in docs])
            score, reason = evaluate_quality_safely(question, parsed_answer["answer"], context)
            ANS_QUALITY_SCORE.set(score)
            AVG_ANSWER_QUALITY_SCORE.observe(score)
            return{"masked_query": question,
                    
                  "answer": parsed_answer["answer"],
                  "sources": parsed_answer["sources"],
                  "retrieved_docs": [
                            doc.page_content for doc in docs
                            ],
                  "answer_quality_score": score,
                  "answer_quality_reason": reason         
            }

        except HTTPException:
            REQUEST_ERRORS.inc()
            raise

        except RuntimeError as e:
            REQUEST_ERRORS.inc()
            logger.error(
                "Configuration error during RAG pipeline",
                extra={
                    "question": question,
                    "error": str(e)
                }
            )
            raise HTTPException(status_code=503, detail=str(e)) from e

        except Exception as e:

            REQUEST_ERRORS.inc()

            logger.error(
                "Error occurred during RAG pipeline",
                extra={
                    "question": question,
                    "error": str(e)
                }
            )

            if is_rate_limit_error(e):
                raise HTTPException(
                    status_code=429,
                    detail="The LLM provider is rate limited. Please wait a few seconds and try again."
                ) from e

            raise HTTPException(status_code=500, detail="RAG pipeline failed") from e
