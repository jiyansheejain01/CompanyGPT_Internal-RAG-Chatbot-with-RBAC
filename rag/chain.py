from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from monitoring.token_tracker import log_token_usage
from monitoring.langsmith_setup import setup_langsmith
setup_langsmith()

from rag.llm_client import get_llm
from rag.prompt_templates import RAG_PROMPT
from retrieval.qdrant_store import search_documents, store_documents
from retrieval.reranker import rerank_documents
from ingestion.embedder import get_embedding_model
from auth.rbac import get_allowed_departments
from guardrails.pii_detector import mask_pii
from guardrails.scope_checker import is_query_in_scope
from guardrails.output_validator import is_answer_grounded

_ingestion_done = False


def ensure_ingestion():
    global _ingestion_done
    if not _ingestion_done:
        from ingestion.ingest_pipeline import run_ingestion
        run_ingestion()
        _ingestion_done = True


def format_context(documents: list[Document]) -> str:
    context_parts = []
    for i, doc in enumerate(documents):
        context_parts.append(
            f"[Source {i+1} | Dept: {doc.metadata.get('department','').upper()} "
            f"| File: {doc.metadata.get('filename','')}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(context_parts)


def run_rag_chain(query: str, role: str) -> dict:
    ensure_ingestion()

    # guardrail 1: scope check
    in_scope, scope_msg = is_query_in_scope(query)
    if not in_scope:
        return {
            "answer": scope_msg,
            "sources": [],
            "role": role,
            "guardrail_triggered": "scope",
            "allowed_departments": []
        }

    # guardrail 2: mask PII in query
    clean_query, pii_found = mask_pii(query)
    if pii_found:
        print(f"PII detected and masked in query.")

    # step 1: RBAC — get allowed departments
    allowed_departments = get_allowed_departments(role)

    # step 2: embed query
    model = get_embedding_model()
    query_embedding = model.encode(clean_query).tolist()

    # step 3: retrieve with RBAC filter
    retrieved_docs = search_documents(
        query_embedding=query_embedding,
        allowed_departments=allowed_departments,
        top_k=15
    )

    if not retrieved_docs:
        return {
            "answer": "I could not find any relevant information in the documents you have access to.",
            "sources": [],
            "role": role,
            "guardrail_triggered": None,
            "allowed_departments": allowed_departments
        }

    # step 4: rerank
    reranked_docs = rerank_documents(
        query=clean_query,
        documents=retrieved_docs,
        top_n=7
    )

    # step 5: generate answer with token tracking
    context = format_context(reranked_docs)
    llm = get_llm()
    chain = RAG_PROMPT | llm | StrOutputParser()

    from langchain_core.callbacks import CallbackManager
    with_cb = llm.with_config({"callbacks": []})
    response = llm.invoke(
        RAG_PROMPT.format_messages(context=context, question=clean_query)
    )
    answer = str(response.content)

    # log tokens
    if hasattr(response, "response_metadata"):
        usage = response.response_metadata.get("token_usage", {})
        log_token_usage(
            username="system",
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0)
        )

    # guardrail 3: output grounding check
    is_grounded, grounding_msg = is_answer_grounded(answer, reranked_docs)
    if not is_grounded:
        print(f"Grounding warning: {grounding_msg}")

    # guardrail 4: mask PII in output
    clean_answer, output_pii = mask_pii(answer)
    if output_pii:
        print("PII masked in output.")

    sources = list(set([
        doc.metadata.get("filename", "unknown")
        for doc in reranked_docs
    ]))

    return {
        "answer": clean_answer,
        "sources": sources,
        "role": role,
        "guardrail_triggered": None,
        "allowed_departments": allowed_departments,
        "pii_detected": pii_found or output_pii,
        "grounded": is_grounded
    }


if __name__ == "__main__":
    # test in-scope query
    result = run_rag_chain(
        query="What is the employee leave policy?",
        role="hr"
    )
    print("\n--- ANSWER ---")
    print(result["answer"])
    print("\n--- SOURCES ---")
    print(result["sources"])
    print("\n--- META ---")
    print(f"Grounded       : {result['grounded']}")
    print(f"PII detected   : {result['pii_detected']}")
    print(f"Departments    : {result['allowed_departments']}")

    # test out-of-scope query
    print("\n\n--- TESTING OUT OF SCOPE ---")
    result2 = run_rag_chain(
        query="Who won the IPL match yesterday?",
        role="hr"
    )
    print(result2["answer"])
