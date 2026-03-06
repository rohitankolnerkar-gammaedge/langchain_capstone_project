from fastapi import FastAPI, UploadFile, Form, APIRouter, HTTPException
from dotenv import load_dotenv
from app.rag.chain import create_rag_chain
from app.guard_rails.input_guardrails import validate_length
from app.guard_rails.pii_masking import PIIGuard
from app.guard_rails.prompt_injection import PromptInjectionGuard
from app.guard_rails.grounding_validator import GroundingValidator
from app.monitoring.looger import logger
from app.rag.conversational_buffer import buffer_memory
load_dotenv()

from app.rag.retreiver import get_retriever
import time

from app.monitoring.timing_callback import TimingCallbackHandler
from app.monitoring.mertics import REQUEST_COUNT,REQUEST_ERRORS,TOTAL_LATENCY,GROUNDED_ANSWERS,UNGROUNDED_ANSWERS,RETRIEVAL_LATENCY
from opentelemetry.trace import Tracer
from app.helper.config_opentelemetry import trace

input_query = APIRouter()

guard = PIIGuard()
detect = PromptInjectionGuard()
validator = GroundingValidator()
memory = buffer_memory()


tracer: Tracer = trace.get_tracer(__name__)


@input_query.post("/question")
async def question(question: str = Form(...), role: str = Form(...)):

    logger.info(
        "RAG request started",
        extra={"question": question, "role": role}
    )

    REQUEST_COUNT.inc()
    total_start = time.perf_counter()
    history = memory.load_memory_variables({})["chat_history"]

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
                callback = TimingCallbackHandler()
                
                llm_start = time.perf_counter()

                response = await chain.ainvoke(
                    {
                        "context": context_text,
                        "question": question,
                        "chat_history": history
                    },
                    config={"callbacks": [callback]}
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

            
            # with tracer.start_as_current_span("Grounding_Validation") as grounding_span:

            #     validation = await validator.validate(context_text, answer)

            #     grounding_span.set_attribute(
            #         "grounded", validation["grounded"]
            #     )

            #     logger.info(
            #         "Grounding validation finished",
            #         extra={
            #             "grounded": validation["grounded"]
            #         }
            #     )

            #     if not validation["grounded"]:

            #         UNGROUNDED_ANSWERS.inc()

            #         end_time = time.perf_counter()
            #         total_latency = end_time - total_start

            #         TOTAL_LATENCY.observe(total_latency)

            #         logger.warning(
            #             "Ungrounded answer detected",
            #             extra={
            #                 "question": question,
            #                 "reason": validation["reason"]
            #             }
            #         )

            #         return {
            #             "error": "Answer not grounded",
            #             "reason": validation["reason"],
            #             "retrieved_docs": [
            #                 doc.page_content for doc in docs
            #             ]
            #         }

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

            return {
                "masked_query": question,
                "answer": answer
            }

        except Exception as e:

            REQUEST_ERRORS.inc()

            logger.error(
                "Error occurred during RAG pipeline",
                extra={
                    "question": question,
                    "error": str(e)
                }
            )

            raise e