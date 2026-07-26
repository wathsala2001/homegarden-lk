import streamlit as st

from core.orchestrator import get_workflow_progress, run_garden_workflow


st.set_page_config(
    page_title="HomeGarden LK",
    page_icon="🌱",
    layout="wide",
)


def get_source_name(item, number):
    """Get a readable source name from retrieved evidence."""

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


def display_list(items):
    """Display a normal Python list in Streamlit."""

    if not items:
        st.write("No information available.")

    elif isinstance(items, list):
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


# Sidebar
with st.sidebar:
    st.title("🌱 HomeGarden LK")

    st.write(
        "HomeGarden LK searches gardening documents and gives "
        "simple home-gardening guidance for Sri Lankan households."
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


# Main page
st.title("🌿 HomeGarden LK")

st.caption(
    "An Agentic AI Home Gardening Assistant for Sri Lankan Households"
)

st.info(
    "Ask questions about planting, watering, fertiliser, soil, pests, "
    "plant diseases, composting and harvesting."
)

st.subheader("Ask a Gardening Question")

user_question = st.text_area(
    "Enter your home-gardening question:",
    placeholder="Example: How often should I water tomato plants?",
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


if ask_button:
    if not user_question.strip():
        st.warning("Please enter a gardening question.")

    else:
        with st.spinner(
            "The three AI agents are working on your question..."
        ):
            state = run_garden_workflow(user_question)

        if state.get("error"):
            st.error(state["error"])

        else:
            st.success("The gardening answer is ready.")

            st.subheader("Your Question")
            st.write(user_question)

            st.subheader("HomeGarden LK Answer")

            final_answer = state.get("final_answer", "")

            if final_answer:
                st.write(final_answer)
            else:
                st.warning(
                    "The system completed the workflow, but no final "
                    "answer was created."
                )

            # Workflow progress
            st.subheader("Agent Workflow")

            progress_messages = get_workflow_progress(state)

            if progress_messages:
                for number, message in enumerate(
                    progress_messages,
                    start=1,
                ):
                    st.write(f"✅ Step {number}: {message}")
            else:
                st.write("No workflow progress was recorded.")

            # Agent 1 information
            with st.expander("Agent 1 – Query Planner Details"):
                st.write(
                    "**Detected plant:**",
                    state.get("plant", "unknown"),
                )

                st.write(
                    "**Question type:**",
                    state.get("question_type", "unknown"),
                )

                st.write("**Search plan:**")
                display_list(state.get("plan", []))

                search_queries = state.get("search_queries", [])

                if search_queries:
                    st.write("**Search queries:**")
                    display_list(search_queries)

            # Agent 2 information
            with st.expander("Agent 2 – Retrieval Details"):
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
                    st.write("**Top retrieved evidence:**")

                    for number, item in enumerate(
                        ranked_evidence[:5],
                        start=1,
                    ):
                        if isinstance(item, dict):
                            evidence_text = (
                                item.get("text")
                                or item.get("content")
                                or item.get("chunk")
                                or "Evidence text not available."
                            )

                            score = (
                                item.get("rerank_score")
                                or item.get("score")
                                or item.get("similarity")
                            )

                            st.markdown(
                                f"**Evidence {number}**"
                            )

                            st.write(evidence_text)

                            if score is not None:
                                st.caption(
                                    f"Relevance score: {score}"
                                )

                        else:
                            st.write(
                                f"**Evidence {number}:** {item}"
                            )

            # Agent 3 information
            with st.expander("Agent 3 – Review Details"):
                reflection = state.get("reflection", {})

                if reflection:
                    if isinstance(reflection, dict):
                        st.write(
                            "**Answer supported by documents:**",
                            reflection.get(
                                "supported",
                                reflection.get(
                                    "is_supported",
                                    "Not recorded",
                                ),
                            ),
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
                            reflection.get("reason")
                            or reflection.get("notes")
                            or reflection.get("feedback")
                        )

                        if review_notes:
                            st.write(
                                "**Review notes:**",
                                review_notes,
                            )

                    else:
                        st.write(reflection)

                else:
                    st.write(
                        "The answer was reviewed before it was displayed."
                    )

            # Sources
            st.subheader("Sources")

            sources = state.get("sources", [])
            ranked_evidence = state.get("ranked_evidence", [])

            if sources:
                for number, source in enumerate(
                    sources,
                    start=1,
                ):
                    if isinstance(source, dict):
                        source_name = get_source_name(
                            source,
                            number,
                        )
                    else:
                        source_name = str(source)

                    st.write(f"{number}. {source_name}")

            elif ranked_evidence:
                shown_sources = []

                for number, item in enumerate(
                    ranked_evidence,
                    start=1,
                ):
                    source_name = get_source_name(
                        item,
                        number,
                    )

                    if source_name not in shown_sources:
                        shown_sources.append(source_name)

                for number, source_name in enumerate(
                    shown_sources,
                    start=1,
                ):
                    st.write(f"{number}. {source_name}")

            else:
                st.write(
                    "No source names were returned by the workflow."
                )

            st.caption(
                f"Workflow status: "
                f"{state.get('status', 'completed')}"
            )


st.divider()

st.caption(
    "HomeGarden LK provides general gardening information. "
    "Follow official product labels when using fertilisers or pesticides."
)