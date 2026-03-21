def is_answer_grounded(answer: str, retrieved_docs: list) -> tuple[bool, str]:
    if not retrieved_docs:
        return False, "No source documents were retrieved."

    if "i don't have enough information" in answer.lower():
        return True, ""

    context_text = " ".join([doc.page_content.lower() for doc in retrieved_docs])
    answer_words = set(answer.lower().split())
    context_words = set(context_text.split())

    overlap = answer_words.intersection(context_words)
    overlap_ratio = len(overlap) / max(len(answer_words), 1)

    if overlap_ratio < 0.15:
        return False, "Answer may not be grounded in the source documents."

    return True, ""
