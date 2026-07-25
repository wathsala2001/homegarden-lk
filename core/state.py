from typing import Any, Dict, List, Optional, TypedDict
from uuid import uuid4


class GardenState(TypedDict):
    """
    Structured message shared by the three HomeGarden LK agents.
    """

    request_id: str
    user_question: str
    plant: str
    question_type: str
    language: str

    plan: List[str]
    search_queries: List[str]

    retrieved_chunks: List[Dict[str, Any]]
    ranked_evidence: List[Dict[str, Any]]

    draft_answer: str
    reflection: Dict[str, Any]
    final_answer: str
    sources: List[Dict[str, Any]]

    status: str
    error: Optional[str]


def create_initial_state(user_question: str) -> GardenState:
    """
    Create the first structured message for a user question.
    """

    return GardenState(
        request_id=f"REQ-{uuid4().hex[:8].upper()}",
        user_question=user_question.strip(),
        plant="unknown",
        question_type="general_gardening",
        language="English",
        plan=[],
        search_queries=[],
        retrieved_chunks=[],
        ranked_evidence=[],
        draft_answer="",
        reflection={
            "supported_by_sources": False,
            "answers_question": False,
            "needs_revision": False,
            "comments": "",
        },
        final_answer="",
        sources=[],
        status="created",
        error=None,
    )