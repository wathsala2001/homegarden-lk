import re
from typing import Any, Dict, List

from core.state import GardenState


MAX_EVIDENCE_ITEMS = 3
MAX_TEXT_LENGTH = 500


def clean_text(text: str) -> str:
    """
    Remove unnecessary spaces and line breaks from evidence text.
    """

    return re.sub(r"\s+", " ", text).strip()


def shorten_text(
    text: str,
    max_length: int = MAX_TEXT_LENGTH,
) -> str:
    """
    Shorten a long evidence chunk without cutting it badly.
    """

    cleaned_text = clean_text(text)

    if len(cleaned_text) <= max_length:
        return cleaned_text

    shortened = cleaned_text[:max_length]

    if "." in shortened:
        shortened = shortened.rsplit(".", 1)[0] + "."

    return shortened


def create_evidence_points(
    evidence: List[Dict[str, Any]],
) -> List[str]:
    """
    Convert the strongest document chunks into readable points.
    """

    evidence_points: List[str] = []

    for item in evidence[:MAX_EVIDENCE_ITEMS]:
        text = shorten_text(str(item.get("text", "")))

        if text:
            evidence_points.append(text)

    return evidence_points


def generate_draft_answer(state: GardenState) -> str:
    """
    Generate a first answer using only retrieved document evidence.
    """

    evidence = state["ranked_evidence"]

    if not evidence:
        return ""

    plant = state["plant"]
    question_type = state["question_type"].replace("_", " ")

    plant_name = (
        plant.title()
        if plant != "unknown"
        else "General home gardening"
    )

    evidence_points = create_evidence_points(evidence)

    answer_parts = [
        f"Plant: {plant_name}",
        f"Question type: {question_type.title()}",
        "",
        "Information found in the gardening documents:",
    ]

    for number, point in enumerate(evidence_points, start=1):
        answer_parts.append(f"{number}. {point}")

    answer_parts.extend(
        [
            "",
            "Recommended action:",
            (
                "Use the information above carefully and compare it "
                "with the current condition of your plant."
            ),
            "",
            (
                "Safety note: Follow official product labels when "
                "using fertilisers or pesticides."
            ),
        ]
    )

    return "\n".join(answer_parts)


def reflect_on_answer(
    state: GardenState,
) -> Dict[str, Any]:
    """
    Reflection pattern:
    Check whether the draft answer is supported and complete.
    """

    draft_answer = state["draft_answer"]
    evidence = state["ranked_evidence"]
    sources = state["sources"]

    supported_by_sources = bool(draft_answer and evidence)
    answers_question = bool(
        draft_answer
        and state["user_question"]
        and state["question_type"]
    )
    has_sources = bool(sources)

    needs_revision = not (
        supported_by_sources
        and answers_question
        and has_sources
    )

    comments: List[str] = []

    if not supported_by_sources:
        comments.append(
            "The answer does not have enough supporting evidence."
        )

    if not answers_question:
        comments.append(
            "The answer does not clearly address the question."
        )

    if not has_sources:
        comments.append(
            "The answer does not include document sources."
        )

    if not comments:
        comments.append(
            "The answer is supported by the retrieved documents."
        )

    return {
        "supported_by_sources": supported_by_sources,
        "answers_question": answers_question,
        "has_sources": has_sources,
        "needs_revision": needs_revision,
        "comments": " ".join(comments),
    }


def prepare_source_text(
    sources: List[Dict[str, Any]],
) -> str:
    """
    Convert the structured sources into readable text.
    """

    if not sources:
        return "No supporting sources were found."

    source_lines = ["Sources:"]

    for number, source in enumerate(sources, start=1):
        document_name = source.get(
            "source",
            "Unknown document",
        )
        page = source.get("page", "Unknown")

        source_lines.append(
            f"{number}. {document_name}, page {page}"
        )

    return "\n".join(source_lines)


def prepare_final_answer(state: GardenState) -> str:
    """
    Prepare the final reviewed answer with sources.
    """

    draft_answer = state["draft_answer"]
    reflection = state["reflection"]

    if not draft_answer:
        return (
            "I could not prepare a reliable answer because "
            "there was not enough document evidence."
        )

    if reflection.get("needs_revision", False):
        return (
            "I could not confirm enough reliable information "
            "from the current gardening documents. Please ask "
            "a more specific gardening question."
        )

    source_text = prepare_source_text(state["sources"])

    return (
        f"{draft_answer}\n\n"
        f"{source_text}\n\n"
        "Answer review: "
        f"{reflection.get('comments', '')}"
    )


def run_answer_review_agent(
    state: GardenState,
) -> GardenState:
    """
    Run Agent 3: Gardening Answer and Review Agent.
    """

    if state["error"]:
        return state

    if not state["ranked_evidence"]:
        state["status"] = "insufficient_evidence"
        state["error"] = (
            "The answer agent did not receive enough "
            "gardening evidence."
        )
        return state

    try:
        state["draft_answer"] = generate_draft_answer(state)

        state["reflection"] = reflect_on_answer(state)

        state["final_answer"] = prepare_final_answer(state)

        if state["reflection"]["needs_revision"]:
            state["status"] = "answer_needs_revision"
        else:
            state["status"] = "answer_complete"

        state["error"] = None

    except Exception as error:
        state["status"] = "error"
        state["error"] = (
            "The answer and review agent failed: "
            f"{error}"
        )

    return state