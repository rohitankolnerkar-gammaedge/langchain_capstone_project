from fastapi import APIRouter
from app.monitoring.evaluate_retreval import evaluate_retrieval
from app.rag.retreiver import get_retriever
from app.monitoring.mertics import RETRIEVAL_ACCURACY
from app.monitoring.test_data import load_test_data
from app.monitoring.evaluate_ans_quality import evaluate_answer_quality
from app.rag.chain import create_rag_chain
from app.llm import get_llm
eval_router = APIRouter()

@eval_router.post("/evaluate")
async def evaluate():

    test_data = load_test_data
    rag_chain = create_rag_chain()
    llm = get_llm()

    retriever = get_retriever( "admin")

    correct, accuracy = evaluate_retrieval(
        test_data,
        retriever
    ) 
    correct_answers, answer_quality = evaluate_answer_quality(
    test_data,
    rag_chain,
    retriever,
    llm
)


    RETRIEVAL_ACCURACY.set(accuracy)

    return {
        "total_questions": len(test_data),
        "correct_retrievals": correct,
        "retrieval_accuracy": accuracy,
        "correct_answers": correct_answers,
        "answer_quality": answer_quality
    }