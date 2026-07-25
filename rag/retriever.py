"""Search the gardening vector store for relevant document chunks."""

from typing import Any

import numpy as np

from rag.embedding_manager import create_query_embedding
from rag.vector_store import load_vector_store


def search_documents(
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Search the local vector store using cosine similarity.

    Args:
        query: User's gardening question.
        top_k: Number of relevant chunks to return.

    Returns:
        Relevant document chunks ordered by similarity.
    """

    if not query.strip():
        raise ValueError("The search query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    embeddings, chunks = load_vector_store()

    if len(chunks) == 0:
        raise ValueError("The vector store contains no document chunks.")

    query_embedding = create_query_embedding(query)

    # Embeddings are normalised, so dot product gives cosine similarity.
    similarity_scores = np.dot(
        embeddings,
        query_embedding,
    )

    result_count = min(top_k, len(chunks))

    best_indices = np.argsort(
        similarity_scores
    )[::-1][:result_count]

    results: list[dict[str, Any]] = []

    for rank, index in enumerate(best_indices, start=1):
        chunk = chunks[int(index)]

        results.append(
            {
                "rank": rank,
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "source": chunk["source"],
                "page": chunk["page"],
                "chunk_number": chunk["chunk_number"],
                "similarity_score": round(
                    float(similarity_scores[index]),
                    4,
                ),
            }
        )

    return results


if __name__ == "__main__":
    test_query = "How should tomato plants be watered?"

    search_results = search_documents(
        query=test_query,
        top_k=5,
    )

    print("=" * 60)
    print("HomeGarden LK Retrieval Test")
    print("=" * 60)

    print(f"Question: {test_query}")
    print(f"Results returned: {len(search_results)}")

    for result in search_results:
        print("\n" + "-" * 60)
        print(f"Rank: {result['rank']}")
        print(f"Source: {result['source']}")
        print(f"Page: {result['page']}")
        print(
            f"Similarity score: "
            f"{result['similarity_score']}"
        )
        print(
            f"Text preview: "
            f"{result['text'][:250]}..."
        )

    print("\n" + "=" * 60)