from typing import List

from agents.answer_review_agent import run_answer_review_agent
from agents.query_planner_agent import run_query_planner
from agents.retrieval_agent import run_retrieval_agent
from core.state import GardenState, create_initial_state


def run_garden_workflow(user_question: str) -> GardenState:
    """
    Run the complete HomeGarden LK agent workflow.

    Workflow:
    1. Create the structured agent state.
    2. Run the Query Planner Agent.
    3. Run the Knowledge Retrieval Agent.
    4. Run the Answer and Review Agent.
    5. Return the final structured state.
    """

    state = create_initial_state(user_question)

    if not user_question.strip():
        state["status"] = "error"
        state["error"] = "Please enter a gardening question."
        return state

    try:
        # Agent 1: Router and Planning patterns.
        state = run_query_planner(state)

        if state["error"]:
            return state

        # Agent 2: ReAct and Tool-Use pattern.
        state = run_retrieval_agent(state)

        if state["error"]:
            return state

        # Agent 3: Reflection and Self-checking pattern.
        state = run_answer_review_agent(state)

        return state

    except Exception as error:
        state["status"] = "error"
        state["error"] = (
            "The HomeGarden LK workflow failed: "
            f"{error}"
        )

        return state


def get_workflow_progress(state: GardenState) -> List[str]:
    """
    Return readable progress messages for the Streamlit interface.
    """

    progress: List[str] = []

    if state["plant"] != "unknown":
        progress.append(
            f"Question classified: {state['question_type']}"
        )

    if state["plan"]:
        progress.append("Search plan created")

    if state["retrieved_chunks"]:
        progress.append("Gardening documents searched")

    if state["ranked_evidence"]:
        progress.append("Relevant evidence ranked")

    if state["final_answer"]:
        progress.append("Final answer reviewed")

    return progress