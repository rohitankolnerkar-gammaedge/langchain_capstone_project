
from app.rag.conversational_buffer import buffer_memory


memory = buffer_memory()

history = memory.load_memory_variables({})["chat_history"]
def evaluate_answer_quality(test_data, rag_chain, retriever, llm):

    correct_answers = 0
    total_questions = len(test_data)

    for item in test_data:

        question = item["question"]

       
        docs = retriever.invoke(question)

        context = "\n".join([
            doc.page_content for doc in docs
        ])

    
        ans = rag_chain.invoke({
            "context": context,
            "question": question,
            "chat_history": history
        })

        prompt = f"""
        Compare the answers.

        Question: {question}

        Ground Truth: {item['ground_truth_answer']}

        Model Answer: {ans}

        Is the model answer correct? Answer YES or NO.
        """

        result = llm.invoke(prompt).content

        if "YES" in result.upper():
            correct_answers += 1

    answer_quality = correct_answers / total_questions if total_questions > 0 else 0

    return correct_answers, answer_quality