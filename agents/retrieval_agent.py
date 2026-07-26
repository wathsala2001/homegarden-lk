import json
from typing import Any, Dict, List, Tuple

from core.prompts import RERANK_SYSTEM_PROMPT
from core.state import GardenState
from models.model_manager import call_rerank_model
from rag.retriever import search_documents


TOP_K_PER_QUERY = 5
FINAL_EVIDENCE_COUNT = 5
MAX_MODEL_CHUNKS = 12


def use_retrieval_tool(
    query: str,
    top_k: int = TOP_K_PER_QUERY,
) -> List[Dict[str, Any]]:
    """
    Search the HomeGarden LK knowledge base.
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
    Convert one search result into the shared structure.
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
        "text": str(result.get("text", "")).strip(),
        "source": str(
            result.get("source", "Unknown document")
        ),
        "page": result.get("page", "Unknown"),
        "similarity_score": score,
        "search_query": search_query,
        "tool_step": tool_step,
    }


def remove_duplicate_chunks(
    chunks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Remove duplicate results returned by different searches.
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


def rank_by_similarity(
    chunks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Rank chunks using their vector similarity scores.
    """

    unique_chunks = remove_duplicate_chunks(chunks)

    return sorted(
        unique_chunks,
        key=lambda item: item.get(
            "similarity_score",
            0.0,
        ),
        reverse=True,
    )


def parse_model_json(
    response_text: str,
) -> Dict[str, Any]:
    """
    Convert Model 2's JSON response into a dictionary.
    """

    cleaned_text = response_text.strip()

    cleaned_text = cleaned_text.replace("```json", "")
    cleaned_text = cleaned_text.replace("```JSON", "")
    cleaned_text = cleaned_text.replace("```", "")
    cleaned_text = cleaned_text.strip()

    start_position = cleaned_text.find("{")
    end_position = cleaned_text.rfind("}")

    if start_position == -1 or end_position == -1:
        raise ValueError(
            "Model 2 did not return valid JSON."
        )

    json_text = cleaned_text[
        start_position:end_position + 1
    ]

    result = json.loads(json_text)

    if not isinstance(result, dict):
        raise ValueError(
            "Model 2 response must be a JSON object."
        )

    return result


def format_chunks_for_model(
    chunks: List[Dict[str, Any]],
) -> str:
    """
    Prepare retrieved evidence for Model 2.
    """

    model_data = []

    for index, chunk in enumerate(chunks):
        model_data.append(
            {
                "index": index,
                "source": chunk.get(
                    "source",
                    "Unknown document",
                ),
                "page": chunk.get(
                    "page",
                    "Unknown",
                ),
                "vector_similarity_score": chunk.get(
                    "similarity_score",
                    0.0,
                ),
                "text": str(
                    chunk.get("text", "")
                )[:1000],
            }
        )

    return json.dumps(
        model_data,
        ensure_ascii=False,
        indent=2,
    )


def rerank_with_model(
    question: str,
    chunks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Use Model 2 to rank evidence by relevance.
    """

    if not chunks:
        return []

    user_prompt = (
        "User gardening question:\n"
        f"{question}\n\n"
        "Retrieved gardening evidence:\n"
        f"{format_chunks_for_model(chunks)}"
    )

    model_response = call_rerank_model(
        system_prompt=RERANK_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )

    result = parse_model_json(model_response)

    ranked_items = result.get(
        "ranked_items",
        [],
    )

    if not isinstance(ranked_items, list):
        raise ValueError(
            "Model 2 did not return ranked_items."
        )

    ai_ranked: List[Dict[str, Any]] = []
    used_indexes: set[int] = set()

    for ranked_item in ranked_items:
        if not isinstance(ranked_item, dict):
            continue

        try:
            index = int(ranked_item.get("index"))
        except (TypeError, ValueError):
            continue

        if index < 0 or index >= len(chunks):
            continue

        if index in used_indexes:
            continue

        try:
            relevance_score = float(
                ranked_item.get(
                    "relevance_score",
                    0.0,
                )
            )
        except (TypeError, ValueError):
            relevance_score = 0.0

        relevance_score = max(
            0.0,
            min(1.0, relevance_score),
        )

        selected_chunk = dict(chunks[index])

        selected_chunk["ai_relevance_score"] = (
            relevance_score
        )

        selected_chunk["rerank_reason"] = str(
            ranked_item.get("reason", "")
        ).strip()

        ai_ranked.append(selected_chunk)
        used_indexes.add(index)

    if not ai_ranked:
        raise ValueError(
            "Model 2 did not return usable rankings."
        )

    ai_ranked.sort(
        key=lambda item: item.get(
            "ai_relevance_score",
            0.0,
        ),
        reverse=True,
    )

    # Add chunks that Model 2 did not return.
    for index, chunk in enumerate(chunks):
        if index not in used_indexes:
            fallback_chunk = dict(chunk)

            fallback_chunk["ai_relevance_score"] = (
                fallback_chunk.get(
                    "similarity_score",
                    0.0,
                )
            )

            fallback_chunk["rerank_reason"] = (
                "This item was ranked using vector similarity."
            )

            ai_ranked.append(fallback_chunk)

    return ai_ranked


def create_fallback_query(
    state: GardenState,
) -> str:
    """
    Create another query when too little evidence is found.
    """

    plant = state["plant"]

    question_type = state[
        "question_type"
    ].replace("_", " ")

    if plant != "unknown":
        return (
            f"{plant} cultivation "
            f"{question_type} home garden"
        )

    return (
        f"vegetable home gardening "
        f"{question_type}"
    )


def build_sources(
    evidence: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Create the structured source list for Agent 3.
    """

    sources: List[Dict[str, Any]] = []
    seen_sources: set[Tuple[str, str]] = set()

    for item in evidence:
        source = str(
            item.get("source", "Unknown document")
        )
        page = str(
            item.get("page", "Unknown")
        )

        identity = (source, page)

        if identity in seen_sources:
            continue

        seen_sources.add(identity)

        sources.append(
            {
                "source": source,
                "page": page,
                "similarity_score": item.get(
                    "similarity_score",
                    0.0,
                ),
                "ai_relevance_score": item.get(
                    "ai_relevance_score",
                    0.0,
                ),
            }
        )

    return sources


def run_retrieval_agent(
    state: GardenState,
) -> GardenState:
    """
    Run Agent 2: Gardening Knowledge Retrieval Agent.

    Patterns:
    - ReAct
    - Tool use
    - AI evidence re-ranking
    """

    if state["error"]:
        return state

    search_queries = state["search_queries"]

    if not search_queries:
        search_queries = [state["user_question"]]

    all_results: List[Dict[str, Any]] = []

    try:
        # ReAct: use the RAG search tool.
        for tool_step, query in enumerate(
            search_queries[:3],
            start=1,
        ):
            raw_results = use_retrieval_tool(
                query=query,
                top_k=TOP_K_PER_QUERY,
            )

            for result in raw_results:
                all_results.append(
                    prepare_result(
                        result=result,
                        search_query=query,
                        tool_step=tool_step,
                    )
                )

        candidate_results = rank_by_similarity(
            all_results
        )

        # ReAct retry when insufficient evidence is found.
        if len(candidate_results) < 3:
            fallback_query = create_fallback_query(
                state
            )

            fallback_results = use_retrieval_tool(
                query=fallback_query,
                top_k=TOP_K_PER_QUERY,
            )

            for result in fallback_results:
                all_results.append(
                    prepare_result(
                        result=result,
                        search_query=fallback_query,
                        tool_step=4,
                    )
                )

            candidate_results = rank_by_similarity(
                all_results
            )

        # Model 2 performs AI evidence re-ranking.
        try:
            ranked_results = rerank_with_model(
                question=state["user_question"],
                chunks=candidate_results[
                    :MAX_MODEL_CHUNKS
                ],
            )

        except Exception as model_error:
            ranked_results = candidate_results

            for item in ranked_results:
                item["ai_relevance_score"] = item.get(
                    "similarity_score",
                    0.0,
                )

                item["rerank_reason"] = (
                    "Vector-ranking fallback used because "
                    f"Model 2 failed: {model_error}"
                )

        final_evidence = ranked_results[
            :FINAL_EVIDENCE_COUNT
        ]

        state["retrieved_chunks"] = (
            remove_duplicate_chunks(all_results)
        )

        state["ranked_evidence"] = final_evidence

        state["sources"] = build_sources(
            final_evidence
        )

        if final_evidence:
            state["status"] = "retrieval_complete"
            state["error"] = None
        else:
            state["status"] = "insufficient_evidence"
            state["error"] = (
                "No relevant gardening evidence was found."
            )

    except FileNotFoundError:
        state["status"] = "error"
        state["error"] = (
            "The gardening vector store was not found. "
            "Run the build-index script first."
        )

    except Exception as error:
        state["status"] = "error"
        state["error"] = (
            "The retrieval agent failed: "
            f"{error}"
        )

    return state