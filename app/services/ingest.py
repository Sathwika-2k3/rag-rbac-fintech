import csv
from pathlib import Path

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import DATA_DIR, VECTORSTORE_DIR

COLLECTION_NAME = "finsolve_docs"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)


def load_markdown_files(department: str, folder: Path) -> list[Document]:
    documents = []
    for path in sorted(folder.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for chunk in splitter.split_text(text):
            documents.append(
                Document(page_content=chunk, metadata={"department": department, "source": path.name})
            )
    return documents


def load_csv_rows(department: str, path: Path) -> list[Document]:
    documents = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            text = ", ".join(f"{key}: {value}" for key, value in row.items())
            documents.append(
                Document(page_content=text, metadata={"department": department, "source": path.name})
            )
    return documents


def load_all_documents() -> list[Document]:
    documents = []
    for department_dir in sorted(p for p in DATA_DIR.iterdir() if p.is_dir()):
        department = department_dir.name
        documents.extend(load_markdown_files(department, department_dir))
        for csv_path in sorted(department_dir.glob("*.csv")):
            documents.extend(load_csv_rows(department, csv_path))
    return documents


def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def build_vectorstore() -> None:
    documents = load_all_documents()
    QdrantVectorStore.from_documents(
        documents,
        embedding=get_embeddings(),
        path=str(VECTORSTORE_DIR),
        collection_name=COLLECTION_NAME,
    )


def get_vectorstore() -> QdrantVectorStore:
    return QdrantVectorStore.from_existing_collection(
        collection_name=COLLECTION_NAME,
        embedding=get_embeddings(),
        path=str(VECTORSTORE_DIR),
    )


if __name__ == "__main__":
    build_vectorstore()
    print("Ingestion complete.")
