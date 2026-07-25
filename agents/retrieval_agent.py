from typing import Any, Dict, List, Tuple

from core.state import GardenState
from rag.retriever import search_documents


TOP_K_PER_SEARCH = 5
FINAL_EVIDENCE_COUNT = 5


def use_retrieval_tool(
    query: str,
    top_k: int = TOP_K_PER_SEARCH,
) -> List[Dict[str, Any]]:
    """
    Tool used by Agent 2 to search the gardening knowledge base.
    """

    return search_documents(
        query=query,
        top_k=top_k,
    )


def prepare_result(
    result: Dict[str, Any],
    search_query: str,
    tool_step: int,
) -> Dict[str, Any]:
    """
    Convert a retrieved result into a common structured format.
    """

    score = result.get(
        "similarity_score",
        result.get("score", 0.0),
    )

    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0.0

    return {
        "text": result.get("text", "").strip(),
        "source": result.get("source", "Unknown document"),
        "page": result.get("page", "Unknown"),
        "similarity_score": score,
        "search_query": search_query,
        "tool_step": tool_step,
    }


def remove_duplicate_chunks(
    chunks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Remove duplicate evidence retrieved by different searches.
    """

    unique_chunks: List[Dict[str, Any]] = []
    seen: set[Tuple[str, str, str]] = set()

    for chunk in chunks:
        source = str(chunk.get("source", ""))
        page = str(chunk.get("page", ""))
        text = str(chunk.get("text", "")).strip()

        identity = (
            source,
            page,
            text[:150],
        )

        if text and identity not in seen:
            seen.add(identity)
            unique_chunks.append(chunk)

    return unique_chunks


def rank_evidence(
    chunks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Rank the retrieved chunks using their similarity scores.
    """

    unique_chunks = remove_duplicate_chunks(chunks)

    return sorted(
        unique_chunks,
        key=lambda item: item.get("similarity_score", 0.0),
        reverse=True,
    )


def create_fallback_query(state: GardenState) -> str:
    """
    Create another search query when the first searches are weak.
    """

    plant = state["plant"]
    question_type = state["question_type"].replace("_", " ")

    if plant != "unknown":
        return f"{plant} cultivation {question_type} home garden"

    return f"vegetable home gardening {question_type}"


def build_sources(
    evidence: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Prepare a clean source list for the final answer.
    """

    sources: List[Dict[str, Any]] = []
    seen_sources: set[Tuple[str, str]] = set()

    for item in evidence:
        source = str(item.get("source", "Unknown document"))
        page = str(item.get("page", "Unknown"))

        source_identity = (source, page)

        if source_identity not in seen_sources:
            seen_sources.add(source_identity)

            sources.append(
                {
                    "source": source,
                    "page": page,
                    "similarity_score": item.get(
                        "similarity_score",
                        0.0,
                    ),
                }
            )

    return sources


def run_retrieval_agent(state: GardenState) -> GardenState:
    """
    Run Agent 2: Gardening Knowledge Retrieval Agent.

    ReAct process:
    1. Read the search plan.
    2. Act by using the retrieval tool.
    3. Observe the returned chunks.
    4. Search again when evidence is weak.
    5. Rank and return the strongest evidence.
    """

    if state["error"]:
        return state

    search_queries = state["search_queries"]

    if not search_queries:
        search_queries = [state["user_question"]]

    all_results: List[Dict[str, Any]] = []

    try:
        # Action and observation for each planned search query.
        for tool_step, query in enumerate(
            search_queries[:3],
            start=1,
        ):
            raw_results = use_retrieval_tool(
                query=query,
                top_k=TOP_K_PER_SEARCH,
            )

            for result in raw_results:
                prepared_result = prepare_result(
                    result=result,
                    search_query=query,
                    tool_step=tool_step,
                )

                all_results.append(prepared_result)

        ranked_results = rank_evidence(all_results)

        # ReAct retry:
        # Search again when fewer than three useful chunks are found.
        if len(ranked_results) < 3:
            fallback_query = create_fallback_query(state)

            fallback_results = use_retrieval_tool(
                query=fallback_query,
                top_k=TOP_K_PER_SEARCH,
            )

            for result in fallback_results:
                prepared_result = prepare_result(
                    result=result,
                    search_query=fallback_query,
                    tool_step=4,
                )

                all_results.append(prepared_result)

            ranked_results = rank_evidence(all_results)

        final_evidence = ranked_results[:FINAL_EVIDENCE_COUNT]

        state["retrieved_chunks"] = all_results
        state["ranked_evidence"] = final_evidence
        state["sources"] = build_sources(final_evidence)

        if final_evidence:
            state["status"] = "retrieval_complete"
            state["error"] = None
        else:
            state["status"] = "insufficient_evidence"
            state["error"] = (
                "No relevant gardening evidence was found "
                "in the knowledge base."
            )

    except FileNotFoundError:
        state["status"] = "error"
        state["error"] = (
            "The gardening vector store was not found. "
            "Run the knowledge-base build script first."
        )

    except Exception as error:
        state["status"] = "error"
        state["error"] = (
            "The retrieval agent could not search the "
            f"gardening knowledge base: {error}"
        )

    return state