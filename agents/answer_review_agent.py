import json
import re
from typing import Any, Dict, List

from core.prompts import (
    ANSWER_SYSTEM_PROMPT,
    REFLECTION_SYSTEM_PROMPT,
)
from core.state import GardenState
from models.model_manager import call_final_model


MAX_EVIDENCE_ITEMS = 5
MAX_TEXT_LENGTH = 1000


def clean_text(text: str) -> str:
    """Remove extra spaces from document text."""

    return re.sub(r"\s+", " ", str(text)).strip()


def shorten_text(
    text: str,
    max_length: int = MAX_TEXT_LENGTH,
) -> str:
    """Shorten very long document chunks."""

    cleaned_text = clean_text(text)

    if len(cleaned_text) <= max_length:
        return cleaned_text

    return cleaned_text[:max_length].rsplit(" ", 1)[0] + "..."


def get_evidence_text(
    evidence: List[Dict[str, Any]],
) -> str:
    """Prepare retrieved evidence for Model 3."""

    evidence_lines: List[str] = []

    for number, item in enumerate(
        evidence[:MAX_EVIDENCE_ITEMS],
        start=1,
    ):
        text = (
            item.get("text")
            or item.get("content")
            or item.get("chunk")
            or ""
        )

        metadata = item.get("metadata", {})

        if not isinstance(metadata, dict):
            metadata = {}

        source = (
            item.get("source")
            or item.get("filename")
            or metadata.get("source")
            or metadata.get("filename")
            or "Unknown document"
        )

        page = (
            item.get("page")
            or metadata.get("page")
            or "Unknown"
        )

        evidence_lines.append(
            f"Evidence {number}\n"
            f"Source: {source}\n"
            f"Page: {page}\n"
            f"Text: {shorten_text(text)}"
        )

    return "\n\n".join(evidence_lines)


def prepare_source_text(
    sources: List[Dict[str, Any]],
) -> str:
    """Convert structured sources into readable text."""

    if not sources:
        return "Sources were not available."

    source_lines = ["Sources:"]

    for number, source in enumerate(sources, start=1):
        metadata = source.get("metadata", {})

        if not isinstance(metadata, dict):
            metadata = {}

        document_name = (
            source.get("source")
            or source.get("filename")
            or metadata.get("source")
            or metadata.get("filename")
            or "Unknown document"
        )

        page = (
            source.get("page")
            or metadata.get("page")
            or "Unknown"
        )

        source_lines.append(
            f"{number}. {document_name}, page {page}"
        )

    return "\n".join(source_lines)


def generate_draft_answer(state: GardenState) -> str:
    """
    Use Model 3 to generate the first gardening answer.
    """

    evidence_text = get_evidence_text(
        state["ranked_evidence"]
    )

    user_prompt = f"""
User question:
{state["user_question"]}

Identified plant:
{state["plant"]}

Question type:
{state["question_type"]}

Retrieved gardening evidence:
{evidence_text}

Write a clear answer in simple English.

Use only the supplied evidence.

Give practical actions when they are supported by the
documents.

Do not invent facts.

Do not create a Sources section because the program will
add the document sources separately.
"""

    answer = call_final_model(
        system_prompt=ANSWER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )

    return answer.strip()


def extract_json(response: str) -> Dict[str, Any]:
    """Convert the model's JSON response into a dictionary."""

    cleaned_response = response.strip()

    cleaned_response = re.sub(
        r"^```(?:json)?",
        "",
        cleaned_response,
        flags=re.IGNORECASE,
    )

    cleaned_response = re.sub(
        r"```$",
        "",
        cleaned_response,
    ).strip()

    json_start = cleaned_response.find("{")
    json_end = cleaned_response.rfind("}")

    if json_start == -1 or json_end == -1:
        raise ValueError(
            "The reflection model did not return valid JSON."
        )

    json_text = cleaned_response[
        json_start:json_end + 1
    ]

    return json.loads(json_text)


def convert_to_boolean(
    value: Any,
    default: bool = False,
) -> bool:
    """Convert JSON values safely into True or False."""

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "yes",
            "1",
        }

    if value is None:
        return default

    return bool(value)


def reflect_on_answer(
    state: GardenState,
) -> Dict[str, Any]:
    """
    Use Model 3 to check the draft answer.
    """

    evidence_text = get_evidence_text(
        state["ranked_evidence"]
    )

    reflection_prompt = f"""
User question:
{state["user_question"]}

Draft answer:
{state["draft_answer"]}

Retrieved evidence:
{evidence_text}

Number of available sources:
{len(state["sources"])}

Check whether the draft answer:

1. Uses the supplied evidence.
2. Answers the user's question.
3. Avoids unsupported claims.
4. Uses simple English.
5. Includes safety advice when required.

Return only the JSON format requested in the system prompt.
"""

    response = call_final_model(
        system_prompt=REFLECTION_SYSTEM_PROMPT,
        user_prompt=reflection_prompt,
        json_mode=True,
    )

    model_review = extract_json(response)

    supported = convert_to_boolean(
        model_review.get(
            "supported_by_sources",
            False,
        )
    )

    answers_question = convert_to_boolean(
        model_review.get(
            "answers_question",
            False,
        )
    )

    has_sources = bool(state["sources"])

    needs_revision = convert_to_boolean(
        model_review.get(
            "needs_revision",
            not (
                supported
                and answers_question
                and has_sources
            ),
        )
    )

    comments = str(
        model_review.get(
            "comments",
            "The answer was checked by Model 3.",
        )
    ).strip()

    return {
        "supported_by_sources": supported,
        "supported": supported,
        "is_supported": supported,
        "answers_question": answers_question,
        "has_sources": has_sources,
        "needs_revision": needs_revision,
        "comments": comments,
    }


def revise_answer(state: GardenState) -> str:
    """
    Use Model 3 to improve an answer when reflection finds
    a problem.
    """

    evidence_text = get_evidence_text(
        state["ranked_evidence"]
    )

    review_comments = state["reflection"].get(
        "comments",
        "Improve the answer.",
    )

    revision_prompt = f"""
User question:
{state["user_question"]}

Current draft answer:
{state["draft_answer"]}

Review comments:
{review_comments}

Retrieved evidence:
{evidence_text}

Rewrite the answer using simple English.

Correct the problems mentioned in the review.

Use only the supplied document evidence.

Do not invent information.

Do not create a Sources section because the program will
add the sources separately.
"""

    revised_answer = call_final_model(
        system_prompt=ANSWER_SYSTEM_PROMPT,
        user_prompt=revision_prompt,
    )

    return revised_answer.strip()


def prepare_final_answer(state: GardenState) -> str:
    """Add sources and review details to the final answer."""

    answer = state["draft_answer"]

    if not answer:
        return (
            "I could not prepare a reliable gardening answer "
            "from the available documents."
        )

    source_text = prepare_source_text(state["sources"])

    review_comment = state["reflection"].get(
        "comments",
        "The answer was reviewed.",
    )

    return (
        f"{answer}\n\n"
        f"{source_text}\n\n"
        f"Answer review: {review_comment}"
    )


def run_answer_review_agent(
    state: GardenState,
) -> GardenState:
    """
    Run Agent 3 using the final AI model.
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
        # Model 3 creates the first answer.
        state["draft_answer"] = generate_draft_answer(
            state
        )

        # Model 3 reviews the answer.
        state["reflection"] = reflect_on_answer(state)

        # Model 3 revises the answer when required.
        if state["reflection"]["needs_revision"]:
            state["draft_answer"] = revise_answer(state)

            # Check the revised answer one more time.
            state["reflection"] = reflect_on_answer(state)

        state["final_answer"] = prepare_final_answer(
            state
        )

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