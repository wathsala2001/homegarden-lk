"""Split extracted gardening documents into smaller text chunks."""

from typing import Any

from rag.document_loader import load_pdf_documents


def split_documents(
    documents: list[dict[str, Any]],
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[dict[str, Any]]:
    """
    Split document pages into overlapping text chunks.

    Args:
        documents: Extracted PDF page records.
        chunk_size: Maximum characters in one chunk.
        overlap: Characters repeated between nearby chunks.

    Returns:
        A list of text chunks with source information.
    """

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0:
        raise ValueError("Overlap cannot be negative.")

    if overlap >= chunk_size:
        raise ValueError(
            "Overlap must be smaller than the chunk size."
        )

    chunks: list[dict[str, Any]] = []

    for document in documents:
        text = document["text"]
        source = document["source"]
        page = document["page"]

        start = 0
        chunk_number = 1

        while start < len(text):
            end = min(start + chunk_size, len(text))

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "chunk_id": (
                            f"{source}-page-{page}-chunk-{chunk_number}"
                        ),
                        "text": chunk_text,
                        "source": source,
                        "page": page,
                        "chunk_number": chunk_number,
                    }
                )

            if end >= len(text):
                break

            start = end - overlap
            chunk_number += 1

    return chunks


if __name__ == "__main__":
    loaded_documents, loading_errors = load_pdf_documents()

    document_chunks = split_documents(
        documents=loaded_documents,
        chunk_size=800,
        overlap=120,
    )

    unique_sources = {
        chunk["source"]
        for chunk in document_chunks
    }

    print("=" * 50)
    print("HomeGarden LK Text Chunking Results")
    print("=" * 50)

    print(
        f"Readable PDF documents: "
        f"{len(unique_sources)}"
    )

    print(
        f"Readable PDF pages: "
        f"{len(loaded_documents)}"
    )

    print(
        f"Total text chunks created: "
        f"{len(document_chunks)}"
    )

    print("Chunk size: 800 characters")
    print("Chunk overlap: 120 characters")

    if loading_errors:
        print(
            f"PDF files with loading errors: "
            f"{len(loading_errors)}"
        )

    if document_chunks:
        first_chunk = document_chunks[0]

        print("\nFirst chunk example:")
        print(f"Source: {first_chunk['source']}")
        print(f"Page: {first_chunk['page']}")
        print(f"Chunk ID: {first_chunk['chunk_id']}")
        print(
            f"Text preview: "
            f"{first_chunk['text'][:200]}..."
        )

    print("=" * 50)