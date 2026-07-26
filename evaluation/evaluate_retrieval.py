import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from rag.retriever import search_documents


QUESTIONS_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "retrieval_questions.json"
)

RESULTS_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "retrieval_results.csv"
)

SUMMARY_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "retrieval_summary.md"
)

TOP_K = 5


def load_questions() -> List[Dict[str, Any]]:
    """
    Load the five retrieval evaluation questions.
    """

    with QUESTIONS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "retrieval_questions.json must contain a list."
        )

    return data


def evaluate_question(
    question_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Search the knowledge base and evaluate one question.
    """

    question = str(
        question_data["question"]
    ).strip()

    expected_keywords = [
        str(keyword).lower().strip()
        for keyword in question_data.get(
            "expected_keywords",
            [],
        )
    ]

    results = search_documents(
        query=question,
        top_k=TOP_K,
    )

    combined_text = " ".join(
        (
            str(result.get("source", ""))
            + " "
            + str(result.get("text", ""))
        ).lower()
        for result in results
    )

    matched_keywords = [
        keyword
        for keyword in expected_keywords
        if keyword in combined_text
    ]

    sources = []

    for result in results:
        source = str(
            result.get(
                "source",
                "Unknown document",
            )
        )

        page = str(
            result.get(
                "page",
                "Unknown",
            )
        )

        sources.append(
            f"{source} page {page}"
        )

    scores = []

    for result in results:
        score = result.get(
            "similarity_score",
            result.get("score", 0.0),
        )

        try:
            scores.append(float(score))
        except (TypeError, ValueError):
            scores.append(0.0)

    best_score = max(scores) if scores else 0.0

    relevant = (
        len(matched_keywords) >= 2
        and bool(results)
    )

    if relevant:
        comment = (
            "Relevant gardening documents were retrieved "
            "and the expected topic keywords were found."
        )
    else:
        comment = (
            "Some results were returned, but the retrieval "
            "may need better keywords or documents."
        )

    return {
        "id": question_data["id"],
        "question": question,
        "expected_keywords": ", ".join(
            expected_keywords
        ),
        "matched_keywords": ", ".join(
            matched_keywords
        ),
        "best_similarity_score": round(
            best_score,
            4,
        ),
        "top_sources": " | ".join(sources),
        "relevant": "Yes" if relevant else "No",
        "comment": comment,
    }


def save_csv(
    results: List[Dict[str, Any]],
) -> None:
    """
    Save evaluation results as a CSV file.
    """

    fieldnames = [
        "id",
        "question",
        "expected_keywords",
        "matched_keywords",
        "best_similarity_score",
        "top_sources",
        "relevant",
        "comment",
    ]

    with RESULTS_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)


def save_summary(
    results: List[Dict[str, Any]],
) -> None:
    """
    Save a readable Markdown evaluation summary.
    """

    relevant_count = sum(
        1
        for result in results
        if result["relevant"] == "Yes"
    )

    total_questions = len(results)

    accuracy = (
        relevant_count / total_questions * 100
        if total_questions
        else 0.0
    )

    lines = [
        "# HomeGarden LK Retrieval Evaluation",
        "",
        f"- Number of questions: {total_questions}",
        f"- Relevant retrievals: {relevant_count}",
        f"- Retrieval success rate: {accuracy:.1f}%",
        f"- Top-K value: {TOP_K}",
        "",
        "## Question Results",
        "",
    ]

    for result in results:
        lines.extend(
            [
                f"### Question {result['id']}",
                "",
                f"**Question:** {result['question']}",
                "",
                (
                    "**Matched keywords:** "
                    f"{result['matched_keywords'] or 'None'}"
                ),
                "",
                (
                    "**Best similarity score:** "
                    f"{result['best_similarity_score']}"
                ),
                "",
                f"**Relevant:** {result['relevant']}",
                "",
                f"**Comment:** {result['comment']}",
                "",
            ]
        )

    SUMMARY_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    """
    Run the complete retrieval evaluation.
    """

    questions = load_questions()

    results = [
        evaluate_question(question)
        for question in questions
    ]

    save_csv(results)
    save_summary(results)

    print("Retrieval evaluation completed.")
    print(f"Questions evaluated: {len(results)}")
    print(f"CSV file: {RESULTS_FILE}")
    print(f"Summary file: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()