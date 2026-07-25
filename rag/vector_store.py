"""Create, save and load the gardening vector store."""

import json
from pathlib import Path
from typing import Any

import numpy as np

from rag.document_loader import load_pdf_documents
from rag.embedding_manager import create_document_embeddings
from rag.text_chunker import split_documents


DEFAULT_VECTOR_FOLDER = Path("data/vector_store")
EMBEDDINGS_FILE = "embeddings.npy"
METADATA_FILE = "metadata.json"


def save_vector_store(
    embeddings: np.ndarray,
    chunks: list[dict[str, Any]],
    output_folder: str | Path = DEFAULT_VECTOR_FOLDER,
) -> None:
    """
    Save embeddings and chunk metadata to the local computer.
    """

    folder = Path(output_folder)
    folder.mkdir(parents=True, exist_ok=True)

    if len(embeddings) != len(chunks):
        raise ValueError(
            "The number of embeddings must match "
            "the number of text chunks."
        )

    embeddings_path = folder / EMBEDDINGS_FILE
    metadata_path = folder / METADATA_FILE

    np.save(
        embeddings_path,
        embeddings.astype(np.float32),
    )

    with metadata_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2,
        )


def load_vector_store(
    vector_folder: str | Path = DEFAULT_VECTOR_FOLDER,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """
    Load the saved embeddings and chunk metadata.
    """

    folder = Path(vector_folder)

    embeddings_path = folder / EMBEDDINGS_FILE
    metadata_path = folder / METADATA_FILE

    if not embeddings_path.exists():
        raise FileNotFoundError(
            "The embeddings file was not found. "
            "Build the vector store first."
        )

    if not metadata_path.exists():
        raise FileNotFoundError(
            "The metadata file was not found. "
            "Build the vector store first."
        )

    embeddings = np.load(
        embeddings_path,
        allow_pickle=False,
    )

    with metadata_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        chunks = json.load(file)

    if len(embeddings) != len(chunks):
        raise ValueError(
            "The saved embeddings and metadata "
            "have different sizes."
        )

    return embeddings, chunks


def create_vector_store(
    chunks: list[dict[str, Any]],
    output_folder: str | Path = DEFAULT_VECTOR_FOLDER,
) -> np.ndarray:
    """
    Create embeddings for all chunks and save the vector store.
    """

    if not chunks:
        raise ValueError(
            "No document chunks were supplied."
        )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print(
        f"Creating embeddings for "
        f"{len(texts)} text chunks..."
    )

    embeddings = create_document_embeddings(texts)

    save_vector_store(
        embeddings=embeddings,
        chunks=chunks,
        output_folder=output_folder,
    )

    return embeddings


if __name__ == "__main__":
    documents, loading_errors = load_pdf_documents()

    document_chunks = split_documents(
        documents=documents,
        chunk_size=800,
        overlap=120,
    )

    vector_embeddings = create_vector_store(
        chunks=document_chunks
    )

    loaded_embeddings, loaded_chunks = (
        load_vector_store()
    )

    print("=" * 55)
    print("HomeGarden LK Vector Store Results")
    print("=" * 55)

    print(
        f"Readable PDF pages: "
        f"{len(documents)}"
    )

    print(
        f"Text chunks saved: "
        f"{len(loaded_chunks)}"
    )

    print(
        f"Embedding matrix shape: "
        f"{loaded_embeddings.shape}"
    )

    print(
        f"Embedding data type: "
        f"{loaded_embeddings.dtype}"
    )

    print(
        f"PDF loading errors: "
        f"{len(loading_errors)}"
    )

    print(
        f"Saved folder: "
        f"{DEFAULT_VECTOR_FOLDER.resolve()}"
    )

    print("Vector store created successfully.")
    print("=" * 55)