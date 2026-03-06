def evaluate_retrieval(test_data, retriever, k=4):
    
    correct_retrievals = 0
    total_questions = len(test_data)

    for item in test_data:

        docs = retriever.invoke(item["question"])

        retrieved_sources = [
            doc.metadata.get("filename")
            for doc in docs
        ]

       
        if item["expected_source"] in retrieved_sources:
            correct_retrievals += 1

    retrieval_accuracy = correct_retrievals / total_questions if total_questions > 0 else 0 

    return correct_retrievals, retrieval_accuracy