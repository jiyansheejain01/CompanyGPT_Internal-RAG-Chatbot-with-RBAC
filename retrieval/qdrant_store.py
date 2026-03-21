import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter,
    FieldCondition, MatchAny
)
from langchain_core.documents import Document

COLLECTION_NAME = "atliq_docs"
VECTOR_SIZE = 384

client = QdrantClient(":memory:")


def create_collection():
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"Collection '{COLLECTION_NAME}' created.")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")


def store_documents(documents: list[Document], embeddings: list[list[float]]):
    create_collection()
    points = []
    for doc, embedding in zip(documents, embeddings):
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "page_content": doc.page_content,
                "department": doc.metadata.get("department", "general"),
                "source": doc.metadata.get("source", ""),
                "filename": doc.metadata.get("filename", ""),
                "file_type": doc.metadata.get("file_type", ""),
            }
        ))
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Stored {len(points)} chunks in Qdrant.")


def search_documents(
    query_embedding: list[float],
    allowed_departments: list[str],
    top_k: int = 10
) -> list[Document]:

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="department",
                    match=MatchAny(any=allowed_departments)
                )
            ]
        ),
        limit=top_k
    )

    documents = []
    for result in results.points:
        documents.append(Document(
            page_content=result.payload["page_content"],
            metadata={
                "department": result.payload["department"],
                "source": result.payload["source"],
                "filename": result.payload["filename"],
                "score": result.score
            }
        ))
    return documents
