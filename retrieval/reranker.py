from flashrank import Ranker, RerankRequest
from langchain_core.documents import Document

ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2")


def rerank_documents(
    query: str,
    documents: list[Document],
    top_n: int = 5
) -> list[Document]:
    if not documents:
        return []

    passages = [
        {"id": i, "text": doc.page_content}
        for i, doc in enumerate(documents)
    ]

    request = RerankRequest(query=query, passages=passages)
    results = ranker.rerank(request)

    reranked = []
    for result in results[:top_n]:
        original_doc = documents[result["id"]]
        original_doc.metadata["rerank_score"] = result["score"]
        reranked.append(original_doc)

    return reranked
