import os
from pathlib import Path
from langchain_core.documents import Document
import csv

DEPARTMENT_FOLDERS = {
    "hr": "hr",
    "finance": "finance",
    "marketing": "marketing",
    "engineering": "engineering",
    "general": "general"
}


def load_markdown_file(file_path: Path, department: str) -> Document:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return Document(
        page_content=content,
        metadata={
            "source": str(file_path),
            "filename": file_path.name,
            "department": department,
            "file_type": "markdown"
        }
    )


def load_csv_file(file_path: Path, department: str) -> list[Document]:
    documents = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            content = " | ".join([f"{k}: {v}" for k, v in row.items()])
            documents.append(Document(
                page_content=content,
                metadata={
                    "source": str(file_path),
                    "filename": file_path.name,
                    "department": department,
                    "file_type": "csv",
                    "row_index": i
                }
            ))
    return documents


def load_documents_from_folder(base_path: str = "data/raw") -> list[Document]:
    all_documents = []
    base = Path(base_path)

    for department, folder_name in DEPARTMENT_FOLDERS.items():
        folder_path = base / folder_name

        if not folder_path.exists():
            print(f"Folder not found, skipping: {folder_path}")
            continue

        print(f"\nLoading department: {department.upper()}")

        for file_path in folder_path.iterdir():
            if file_path.suffix == ".md":
                doc = load_markdown_file(file_path, department)
                all_documents.append(doc)
                print(f"  Loaded: {file_path.name}")

            elif file_path.suffix == ".csv":
                docs = load_csv_file(file_path, department)
                all_documents.extend(docs)
                print(f"  Loaded: {file_path.name} ({len(docs)} rows)")

            else:
                print(f"  Skipped unsupported file: {file_path.name}")

    print(f"\nTotal documents loaded: {len(all_documents)}")
    return all_documents


if __name__ == "__main__":
    docs = load_documents_from_folder()
    for doc in docs[:3]:
        print("\n--- SAMPLE DOC ---")
        print(f"Department : {doc.metadata['department']}")
        print(f"File       : {doc.metadata['filename']}")
        print(f"Content    : {doc.page_content[:200]}")
