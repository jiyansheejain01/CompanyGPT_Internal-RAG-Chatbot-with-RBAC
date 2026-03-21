from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def chunk_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " "]
    )

    chunked_docs = []
    for doc in documents:
        # CSV rows are already small, don't chunk them further
        if doc.metadata.get("file_type") == "csv":
            chunked_docs.append(doc)
            continue

        chunks = splitter.split_documents([doc])
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            chunked_docs.append(chunk)

    print(f"Total chunks created: {len(chunked_docs)}")
    return chunked_docs


if __name__ == "__main__":
    from ingestion.document_loader import load_documents_from_folder
    docs = load_documents_from_folder()
    chunks = chunk_documents(docs)
    print("\n--- SAMPLE CHUNK ---")
    print(f"Department : {chunks[0].metadata['department']}")
    print(f"Content    : {chunks[0].page_content[:300]}")