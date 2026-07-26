import base64
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from core.orchestrator import (
    get_workflow_progress,
    run_garden_workflow,
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="HomeGarden LK",
    page_icon="🌱",
    layout="wide",
)


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def load_banner_image() -> str:
    """
    Load the local gardening banner image
    and convert it into Base64 format.
    """

    image_path = (
        Path(__file__).parent
        / "assets"
        / "garden_banner.png"
    )

    if not image_path.exists():
        return ""

    return base64.b64encode(
        image_path.read_bytes()
    ).decode("utf-8")


def get_source_name(
    item: Any,
    number: int,
) -> str:
    """
    Get a readable document name.
    """

    if not isinstance(item, dict):
        return f"Gardening source {number}"

    metadata = item.get("metadata", {})

    if not isinstance(metadata, dict):
        metadata = {}

    return (
        item.get("source")
        or item.get("filename")
        or item.get("document")
        or metadata.get("source")
        or metadata.get("filename")
        or f"Gardening source {number}"
    )


def get_source_page(item: Any) -> str:
    """
    Get the page number from a source.
    """

    if not isinstance(item, dict):
        return ""

    metadata = item.get("metadata", {})

    if not isinstance(metadata, dict):
        metadata = {}

    page = (
        item.get("page")
        or item.get("page_number")
        or metadata.get("page")
        or metadata.get("page_number")
    )

    if page is None:
        return ""

    return str(page)


def get_source_label(
    item: Any,
    number: int,
) -> str:
    """
    Create a source label with the page number.
    """

    source_name = get_source_name(
        item,
        number,
    )

    page = get_source_page(item)

    if page:
        return f"{source_name}, page {page}"

    return source_name


def display_list(items: Any) -> None:
    """
    Display lists clearly in Streamlit.
    """

    if not items:
        st.write("No information available.")
        return

    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                text = (
                    item.get("query")
                    or item.get("step")
                    or item.get("text")
                    or item.get("content")
                    or str(item)
                )

                st.write(f"- {text}")

            else:
                st.write(f"- {item}")

    else:
        st.write(items)


def display_hero_banner() -> None:
    """
    Display the large HomeGarden LK banner.
    """

    banner_image = load_banner_image()

    if not banner_image:
        st.title("🌿 HomeGarden LK")

        st.caption(
            "An Agentic AI Home Gardening Assistant "
            "for Sri Lankan Households"
        )

        return

    hero_html = f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">

        <style>
            * {{
                box-sizing: border-box;
            }}

            html,
            body {{
                margin: 0;
                padding: 0;
                background: transparent;

                font-family:
                    -apple-system,
                    BlinkMacSystemFont,
                    "Segoe UI",
                    Arial,
                    sans-serif;
            }}

            .hero {{
                width: 100%;
                min-height: 400px;

                display: flex;
                align-items: center;
                justify-content: flex-end;

                padding: 30px;

                border-radius: 18px;
                overflow: hidden;

                background-image:
                    linear-gradient(
                        90deg,
                        rgba(0, 25, 10, 0.02),
                        rgba(0, 45, 18, 0.50)
                    ),
                    url(
                        "data:image/png;base64,{banner_image}"
                    );

                background-size: cover;
                background-position: center;

                box-shadow:
                    0 7px 22px
                    rgba(0, 0, 0, 0.20);
            }}

            .hero-content {{
                width: 49%;
                max-width: 720px;

                padding: 34px;

                border-radius: 17px;

                background:
                    rgba(3, 58, 25, 0.90);

                box-shadow:
                    0 5px 18px
                    rgba(0, 0, 0, 0.22);
            }}

            .hero-tag {{
                display: inline-block;

                margin-bottom: 17px;
                padding: 8px 14px;

                border-radius: 20px;

                background:
                    rgba(255, 255, 255, 0.16);

                color: white;

                font-size: 13px;
                font-weight: 650;
            }}

            .hero-title {{
                margin: 0 0 16px 0;

                color: white;

                font-size: 46px;
                font-weight: 750;
                line-height: 1.15;
            }}

            .hero-text {{
                margin: 0;

                color: #f3fff4;

                font-size: 18px;
                line-height: 1.65;
            }}

            @media
            (max-width: 900px) {{

                .hero {{
                    min-height: 350px;
                    padding: 20px;
                    justify-content: center;
                }}

                .hero-content {{
                    width: 100%;
                    max-width: none;
                    padding: 25px;
                }}

                .hero-title {{
                    font-size: 32px;
                }}

                .hero-text {{
                    font-size: 15px;
                }}
            }}
        </style>
    </head>

    <body>

        <section class="hero">

            <div class="hero-content">

                <div class="hero-tag">
                    Agentic AI Gardening Assistant
                </div>

                <h1 class="hero-title">
                    🌿 HomeGarden LK
                </h1>

                <p class="hero-text">
                    Simple, document-supported home-gardening
                    guidance for Sri Lankan households.
                    Ask questions about planting, watering,
                    fertiliser, soil preparation, pests,
                    plant diseases, composting and harvesting.
                </p>

            </div>

        </section>

    </body>

    </html>
    """

    components.html(
        hero_html,
        height=425,
        scrolling=False,
    )


# ==================================================
# MAIN PAGE STYLING
# ==================================================

st.markdown(
    """
    <style>
        .block-container {
            max-width: 100%;
            padding-top: 0.6rem;
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 3rem;
        }

        section[data-testid="stSidebar"] {
            background-color: #f1f7f2;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #173f25;
        }

        div[data-testid="stButton"] > button {
            width: 100%;

            background-color: #2e7d32;
            color: white;

            border: none;
            border-radius: 9px;

            padding: 0.75rem;

            font-weight: 600;
        }

        div[data-testid="stButton"] > button:hover {
            background-color: #1b5e20;
            color: white;
            border: none;
        }

        div[data-testid="stButton"] > button:focus {
            background-color: #2e7d32;
            color: white;
            border: none;
            box-shadow: none;
        }

        div[data-testid="stAlert"] {
            border-radius: 10px;
        }

        div[data-testid="stExpander"] {
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.title("🌱 HomeGarden LK")

    st.write(
        "HomeGarden LK searches gardening documents "
        "and gives simple home-gardening guidance "
        "for Sri Lankan households."
    )

    st.subheader("Three AI Agents")

    st.write("1. Query Planner Agent")
    st.write("2. Knowledge Retrieval Agent")
    st.write("3. Answer and Review Agent")

    st.subheader("Four Agentic Patterns")

    st.write("- Routing")
    st.write("- Planning")
    st.write("- ReAct / Tool Use")
    st.write("- Reflection")

    st.subheader("Supported Areas")

    st.write(
        "- Planting\n"
        "- Watering\n"
        "- Fertiliser\n"
        "- Soil preparation\n"
        "- Pest control\n"
        "- Plant diseases\n"
        "- Composting\n"
        "- Harvesting"
    )


# ==================================================
# HERO BANNER
# ==================================================

display_hero_banner()


# ==================================================
# QUESTION FORM
# ==================================================

st.info(
    "Ask questions about planting, watering, "
    "fertiliser, soil, pests, plant diseases, "
    "composting and harvesting."
)

st.subheader("Ask a Gardening Question")

user_question = st.text_area(
    "Enter your home-gardening question:",
    placeholder=(
        "Example: How often should I water "
        "tomato plants?"
    ),
    height=100,
)

st.write("**Example questions:**")

st.write(
    "- How can I grow tomatoes in pots?\n"
    "- What fertiliser is suitable for chilli plants?\n"
    "- Why are my brinjal leaves turning yellow?\n"
    "- How can I control aphids naturally?\n"
    "- How can I prepare compost at home?"
)

ask_button = st.button(
    "Ask HomeGarden LK",
    type="primary",
    use_container_width=True,
)


# ==================================================
# RUN THE THREE-AGENT WORKFLOW
# ==================================================

if ask_button:

    if not user_question.strip():

        st.warning(
            "Please enter a gardening question."
        )

    else:

        with st.spinner(
            "The three AI agents are working "
            "on your question..."
        ):

            state = run_garden_workflow(
                user_question
            )

        if state.get("error"):

            st.error(
                state["error"]
            )

        else:

            st.success(
                "The gardening answer is ready."
            )

            st.subheader("Your Question")

            st.write(
                user_question
            )

            st.subheader(
                "HomeGarden LK Answer"
            )

            final_answer = state.get(
                "final_answer",
                "",
            )

            if final_answer:

                st.markdown(
                    final_answer
                )

            else:

                st.warning(
                    "The workflow completed, but no "
                    "final answer was created."
                )


            # ==========================================
            # WORKFLOW PROGRESS
            # ==========================================

            st.subheader(
                "Agent Workflow"
            )

            progress_messages = (
                get_workflow_progress(
                    state
                )
            )

            if progress_messages:

                for number, message in enumerate(
                    progress_messages,
                    start=1,
                ):

                    st.write(
                        f"✅ Step {number}: {message}"
                    )

            else:

                st.write(
                    "No workflow progress "
                    "was recorded."
                )


            # ==========================================
            # AGENT 1 DETAILS
            # ==========================================

            with st.expander(
                "Agent 1 – Query Planner Details"
            ):

                st.write(
                    "**Detected plant:**",
                    state.get(
                        "plant",
                        "unknown",
                    ),
                )

                st.write(
                    "**Question type:**",
                    state.get(
                        "question_type",
                        "unknown",
                    ),
                )

                st.write(
                    "**Search plan:**"
                )

                display_list(
                    state.get(
                        "plan",
                        [],
                    )
                )

                search_queries = state.get(
                    "search_queries",
                    [],
                )

                if search_queries:

                    st.write(
                        "**Search queries:**"
                    )

                    display_list(
                        search_queries
                    )


            # ==========================================
            # AGENT 2 DETAILS
            # ==========================================

            with st.expander(
                "Agent 2 – Retrieval Details"
            ):

                retrieved_chunks = state.get(
                    "retrieved_chunks",
                    [],
                )

                ranked_evidence = state.get(
                    "ranked_evidence",
                    [],
                )

                st.write(
                    "**Retrieved document chunks:**",
                    len(retrieved_chunks),
                )

                st.write(
                    "**Ranked evidence items:**",
                    len(ranked_evidence),
                )

                if ranked_evidence:

                    st.write(
                        "**Top retrieved evidence:**"
                    )

                    for number, item in enumerate(
                        ranked_evidence[:5],
                        start=1,
                    ):

                        if isinstance(item, dict):

                            evidence_text = (
                                item.get("text")
                                or item.get("content")
                                or item.get("chunk")
                                or (
                                    "Evidence text "
                                    "not available."
                                )
                            )

                            score = (
                                item.get("rerank_score")
                                or item.get("score")
                                or item.get("similarity")
                            )

                            source_label = (
                                get_source_label(
                                    item,
                                    number,
                                )
                            )

                            st.markdown(
                                f"**Evidence {number}**"
                            )

                            st.caption(
                                f"Source: {source_label}"
                            )

                            st.write(
                                evidence_text
                            )

                            if score is not None:

                                st.caption(
                                    "Relevance score: "
                                    f"{score}"
                                )

                        else:

                            st.write(
                                f"**Evidence {number}:** "
                                f"{item}"
                            )

                else:

                    st.write(
                        "No ranked evidence "
                        "was returned."
                    )


            # ==========================================
            # AGENT 3 DETAILS
            # ==========================================

            with st.expander(
                "Agent 3 – Review Details"
            ):

                reflection = state.get(
                    "reflection",
                    {},
                )

                if isinstance(
                    reflection,
                    dict,
                ):

                    supported = reflection.get(
                        "supported_by_sources",
                        reflection.get(
                            "supported",
                            reflection.get(
                                "is_supported",
                                "Not recorded",
                            ),
                        ),
                    )

                    st.write(
                        "**Answer supported by documents:**",
                        supported,
                    )

                    st.write(
                        "**Question answered:**",
                        reflection.get(
                            "answers_question",
                            "Not recorded",
                        ),
                    )

                    st.write(
                        "**Sources included:**",
                        reflection.get(
                            "has_sources",
                            "Not recorded",
                        ),
                    )

                    st.write(
                        "**Revision required:**",
                        reflection.get(
                            "needs_revision",
                            "Not recorded",
                        ),
                    )

                    review_notes = (
                        reflection.get("comments")
                        or reflection.get("reason")
                        or reflection.get("notes")
                        or reflection.get("feedback")
                    )

                    if review_notes:

                        st.write(
                            "**Review notes:**",
                            review_notes,
                        )

                elif reflection:

                    st.write(
                        reflection
                    )

                else:

                    st.write(
                        "The answer was reviewed "
                        "before it was displayed."
                    )


            # ==========================================
            # SOURCES
            # ==========================================

            st.subheader(
                "Sources"
            )

            sources = state.get(
                "sources",
                [],
            )

            ranked_evidence = state.get(
                "ranked_evidence",
                [],
            )

            shown_sources = []

            if sources:

                for number, source in enumerate(
                    sources,
                    start=1,
                ):

                    if isinstance(
                        source,
                        dict,
                    ):

                        source_label = (
                            get_source_label(
                                source,
                                number,
                            )
                        )

                    else:

                        source_label = str(
                            source
                        )

                    if (
                        source_label
                        not in shown_sources
                    ):

                        shown_sources.append(
                            source_label
                        )

            elif ranked_evidence:

                for number, item in enumerate(
                    ranked_evidence,
                    start=1,
                ):

                    source_label = (
                        get_source_label(
                            item,
                            number,
                        )
                    )

                    if (
                        source_label
                        not in shown_sources
                    ):

                        shown_sources.append(
                            source_label
                        )

            if shown_sources:

                for number, source_label in enumerate(
                    shown_sources,
                    start=1,
                ):

                    st.write(
                        f"{number}. {source_label}"
                    )

            else:

                st.write(
                    "No source names were returned "
                    "by the workflow."
                )

            st.caption(
                "Workflow status: "
                f"{state.get('status', 'completed')}"
            )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "HomeGarden LK provides general gardening "
    "information. Follow official product labels "
    "when using fertilisers or pesticides."
)