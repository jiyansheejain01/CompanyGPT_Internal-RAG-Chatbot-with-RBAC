from ingestion.document_loader import load_documents_from_folder
from ingestion.chunker import chunk_documents
from ingestion.embedder import embed_documents
from retrieval.qdrant_store import store_documents


def run_ingestion(data_path: str = "data/raw"):
    print("=" * 50)
    print("STEP 1: Loading documents")
    print("=" * 50)
    documents = load_documents_from_folder(data_path)

    print("\n" + "=" * 50)
    print("STEP 2: Chunking documents")
    print("=" * 50)
    chunks = chunk_documents(documents)

    print("\n" + "=" * 50)
    print("STEP 3: Embedding chunks")
    print("=" * 50)
    docs, embeddings = embed_documents(chunks)

    print("\n" + "=" * 50)
    print("STEP 4: Storing in Qdrant")
    print("=" * 50)
    store_documents(docs, embeddings)

    print("\n✅ Ingestion complete!")
    print(f"   Total chunks stored: {len(chunks)}")


if __name__ == "__main__":
    run_ingestion()
