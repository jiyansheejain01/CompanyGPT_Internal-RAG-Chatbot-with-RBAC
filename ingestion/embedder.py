from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document

MODEL_NAME = "all-MiniLM-L6-v2"

# load once, reuse everywhere
_model = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_documents(documents: list[Document]) -> tuple[list[Document], list[list[float]]]:
    model = get_embedding_model()
    texts = [doc.page_content for doc in documents]
    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()
    print("Embedding complete.")
    return documents, embeddings


if __name__ == "__main__":
    from ingestion.document_loader import load_documents_from_folder
    from ingestion.chunker import chunk_documents
    docs = load_documents_from_folder()
    chunks = chunk_documents(docs)
    docs_out, embeddings = embed_documents(chunks)
    print(f"\nEmbedding shape: {len(embeddings)} x {len(embeddings[0])}")
