"""Build the complete HomeGarden LK gardening knowledge base."""

from rag.document_loader import load_pdf_documents
from rag.text_chunker import split_documents
from rag.vector_store import create_vector_store


def build_gardening_index() -> None:
    """Load PDFs, create chunks, generate embeddings and save them."""

    print("=" * 60)
    print("HomeGarden LK Knowledge Base Builder")
    print("=" * 60)

    print("\nStep 1: Loading gardening PDF documents...")

    documents, loading_errors = load_pdf_documents(
        folder_path="data/raw_documents"
    )

    readable_sources = {
        document["source"]
        for document in documents
    }

    print(f"Readable documents found: {len(readable_sources)}")
    print(f"Readable pages found: {len(documents)}")

    print("\nStep 2: Splitting documents into chunks...")

    chunks = split_documents(
        documents=documents,
        chunk_size=800,
        overlap=120,
    )

    print(f"Text chunks created: {len(chunks)}")

    print("\nStep 3: Creating and saving embeddings...")

    embeddings = create_vector_store(
        chunks=chunks,
        output_folder="data/vector_store",
    )

    print("\n" + "=" * 60)
    print("Knowledge Base Build Summary")
    print("=" * 60)

    print(f"Readable documents: {len(readable_sources)}")
    print(f"Readable pages: {len(documents)}")
    print(f"Text chunks: {len(chunks)}")
    print(f"Embedding matrix shape: {embeddings.shape}")
    print(f"PDF loading errors: {len(loading_errors)}")

    if loading_errors:
        print("\nFiles with errors:")

        for item in loading_errors:
            print(f"- {item['source']}: {item['error']}")

    print("\nKnowledge base created successfully.")
    print("=" * 60)


if __name__ == "__main__":
    build_gardening_index()