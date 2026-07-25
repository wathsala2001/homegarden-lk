"""Create numerical embeddings for gardening text."""

from typing import Optional

import numpy as np
from fastembed import TextEmbedding


# Lightweight English embedding model.
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# Store the model after loading it once.
_embedding_model: Optional[TextEmbedding] = None


def get_embedding_model() -> TextEmbedding:
    """
    Load and return the FastEmbed model.

    The model is loaded only once during the program.
    """

    global _embedding_model

    if _embedding_model is None:
        print(
            f"Loading embedding model: "
            f"{EMBEDDING_MODEL_NAME}"
        )

        _embedding_model = TextEmbedding(
            model_name=EMBEDDING_MODEL_NAME
        )

    return _embedding_model


def normalize_embeddings(
    embeddings: np.ndarray,
) -> np.ndarray:
    """
    Normalise vectors for cosine-similarity searching.
    """

    vector_lengths = np.linalg.norm(
        embeddings,
        axis=1,
        keepdims=True,
    )

    # Prevent division by zero.
    vector_lengths[vector_lengths == 0] = 1.0

    return embeddings / vector_lengths


def create_document_embeddings(
    texts: list[str],
) -> np.ndarray:
    """
    Create embeddings for gardening document chunks.
    """

    if not texts:
        raise ValueError(
            "At least one document text is required."
        )

    model = get_embedding_model()

    # The passage prefix identifies these as document texts.
    prepared_texts = [
        f"passage: {text}"
        for text in texts
    ]

    embedding_generator = model.embed(prepared_texts)

    embeddings = np.array(
        list(embedding_generator),
        dtype=np.float32,
    )

    return normalize_embeddings(embeddings)


def create_query_embedding(
    query: str,
) -> np.ndarray:
    """
    Create one embedding for a user's gardening question.
    """

    if not query.strip():
        raise ValueError(
            "The search query cannot be empty."
        )

    model = get_embedding_model()

    # The query prefix identifies this as a search question.
    embedding_generator = model.embed(
        [f"query: {query.strip()}"]
    )

    embedding = np.array(
        list(embedding_generator),
        dtype=np.float32,
    )

    normalised_embedding = normalize_embeddings(
        embedding
    )

    return normalised_embedding[0]


if __name__ == "__main__":
    from rag.document_loader import load_pdf_documents
    from rag.text_chunker import split_documents

    documents, errors = load_pdf_documents()

    chunks = split_documents(
        documents=documents,
        chunk_size=800,
        overlap=120,
    )

    # Use only three chunks for this first test.
    sample_texts = [
        chunk["text"]
        for chunk in chunks[:3]
    ]

    document_embeddings = create_document_embeddings(
        sample_texts
    )

    sample_query = (
        "How should tomato plants be watered?"
    )

    query_embedding = create_query_embedding(
        sample_query
    )

    print("=" * 55)
    print("HomeGarden LK Embedding Test")
    print("=" * 55)
    print(f"Embedding model: {EMBEDDING_MODEL_NAME}")
    print(f"Sample document chunks: {len(sample_texts)}")
    print(
        f"Document embedding shape: "
        f"{document_embeddings.shape}"
    )
    print(
        f"Query embedding shape: "
        f"{query_embedding.shape}"
    )
    print(
        f"Document vector type: "
        f"{document_embeddings.dtype}"
    )
    print("Embedding test completed successfully.")
    print("=" * 55)