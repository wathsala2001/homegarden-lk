import json
from typing import Any, Dict, List

from core.prompts import ROUTER_SYSTEM_PROMPT
from core.state import GardenState
from models.model_manager import call_router_model


# Plants supported by HomeGarden LK.
PLANT_KEYWORDS: Dict[str, List[str]] = {
    "tomato": ["tomato", "tomatoes"],
    "chilli": ["chilli", "chillies", "chili", "pepper"],
    "brinjal": ["brinjal", "eggplant", "aubergine"],
    "okra": ["okra", "ladies finger", "lady's finger"],
    "cucumber": ["cucumber", "cucumbers"],
    "bean": ["bean", "beans"],
    "carrot": ["carrot", "carrots"],
    "mint": ["mint"],
    "gotukola": ["gotukola", "gotu kola"],
    "mukunuwenna": ["mukunuwenna"],
    "kangkung": ["kangkung", "kang kung"],
    "nivithi": ["nivithi", "spinach"],
}


# Keywords used by the Router pattern.
QUESTION_TYPE_KEYWORDS: Dict[str, List[str]] = {
    "watering": [
        "water",
        "watering",
        "irrigation",
        "dry soil",
        "moisture",
    ],
    "fertiliser": [
        "fertiliser",
        "fertilizer",
        "nutrient",
        "compost tea",
        "manure",
        "npk",
    ],
    "pest_control": [
        "pest",
        "aphid",
        "whitefly",
        "whiteflies",
        "caterpillar",
        "insect",
        "beetle",
        "mite",
        "snail",
    ],
    "plant_disease": [
        "disease",
        "yellow leaves",
        "turning yellow",
        "leaf spots",
        "wilting",
        "fungus",
        "mould",
        "mold",
        "root rot",
    ],
    "soil": [
        "soil",
        "potting mix",
        "drainage",
        "ph level",
        "garden bed",
    ],
    "composting": [
        "compost",
        "composting",
        "organic waste",
        "kitchen waste",
    ],
    "harvesting": [
        "harvest",
        "harvesting",
        "pick",
        "picking",
        "ready to collect",
    ],
    "planting": [
        "plant",
        "planting",
        "grow",
        "growing",
        "seed",
        "seedling",
        "nursery",
        "pot",
        "container",
    ],
}


ALLOWED_QUESTION_TYPES = {
    "planting",
    "watering",
    "fertiliser",
    "soil",
    "pest_control",
    "plant_disease",
    "harvesting",
    "composting",
    "general_gardening",
}


def identify_plant(question: str) -> str:
    """
    Identify the plant mentioned in the user's question.
    This function is used as a fallback when the AI model fails.
    """

    question_lower = question.lower()

    for plant, keywords in PLANT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in question_lower:
                return plant

    return "unknown"


def classify_question(question: str) -> str:
    """
    Router pattern:
    Identify the main category of the gardening question.

    This function is used as a fallback when the AI model fails.
    """

    question_lower = question.lower()

    priority_order = [
        "plant_disease",
        "pest_control",
        "watering",
        "fertiliser",
        "soil",
        "composting",
        "harvesting",
        "planting",
    ]

    for question_type in priority_order:
        keywords = QUESTION_TYPE_KEYWORDS[question_type]

        if any(keyword in question_lower for keyword in keywords):
            return question_type

    return "general_gardening"


def create_search_queries(
    question: str,
    plant: str,
    question_type: str,
) -> List[str]:
    """
    Create useful search queries for the RAG knowledge base.
    """

    readable_type = question_type.replace("_", " ")

    queries = [question.strip()]

    if plant != "unknown":
        queries.append(f"{plant} {readable_type}")
        queries.append(
            f"{plant} home gardening {readable_type}"
        )
    else:
        queries.append(
            f"home gardening {readable_type}"
        )

    # Remove duplicate queries while keeping their order.
    return list(dict.fromkeys(queries))


def create_plan(
    plant: str,
    question_type: str,
) -> List[str]:
    """
    Planning pattern:
    Divide the gardening question into smaller tasks.
    """

    plant_name = (
        plant if plant != "unknown" else "the plant"
    )

    readable_type = question_type.replace("_", " ")

    return [
        f"Identify information about {plant_name}.",
        f"Search documents about {readable_type}.",
        "Retrieve the most relevant gardening evidence.",
        "Prepare clear actions supported by the documents.",
    ]


def parse_model_json(
    response_text: str,
) -> Dict[str, Any]:
    """
    Convert the Router model response into a Python dictionary.
    """

    cleaned_text = response_text.strip()

    # Remove Markdown code-block symbols when included.
    cleaned_text = cleaned_text.replace("```json", "")
    cleaned_text = cleaned_text.replace("```JSON", "")
    cleaned_text = cleaned_text.replace("```", "")
    cleaned_text = cleaned_text.strip()

    start_position = cleaned_text.find("{")
    end_position = cleaned_text.rfind("}")

    if start_position == -1 or end_position == -1:
        raise ValueError(
            "The Router model did not return valid JSON."
        )

    json_text = cleaned_text[
        start_position:end_position + 1
    ]

    result = json.loads(json_text)

    if not isinstance(result, dict):
        raise ValueError(
            "The Router model response must be a JSON object."
        )

    return result


def run_ai_planner(
    state: GardenState,
) -> GardenState:
    """
    Use Model 1 to perform routing and planning.
    """

    user_prompt = (
        "Analyse the following home-gardening question.\n\n"
        f"Question: {state['user_question']}"
    )

    model_response = call_router_model(
        system_prompt=ROUTER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )

    result = parse_model_json(model_response)

    plant = str(
        result.get("plant", "unknown")
    ).strip().lower()

    if not plant:
        plant = "unknown"

    question_type = str(
        result.get(
            "question_type",
            "general_gardening",
        )
    ).strip().lower()

    if question_type not in ALLOWED_QUESTION_TYPES:
        question_type = "general_gardening"

    search_queries = result.get(
        "search_queries",
        [],
    )

    plan = result.get(
        "plan",
        [],
    )

    if not isinstance(search_queries, list):
        search_queries = []

    if not isinstance(plan, list):
        plan = []

    clean_search_queries = [
        str(query).strip()
        for query in search_queries
        if str(query).strip()
    ]

    clean_plan = [
        str(task).strip()
        for task in plan
        if str(task).strip()
    ]

    # Create fallback values when the model returns empty lists.
    if not clean_search_queries:
        clean_search_queries = create_search_queries(
            question=state["user_question"],
            plant=plant,
            question_type=question_type,
        )

    if not clean_plan:
        clean_plan = create_plan(
            plant=plant,
            question_type=question_type,
        )

    state["plant"] = plant
    state["question_type"] = question_type
    state["search_queries"] = clean_search_queries
    state["plan"] = clean_plan
    state["status"] = "planning_complete"
    state["error"] = None

    return state


def run_query_planner(
    state: GardenState,
) -> GardenState:
    """
    Run Agent 1: Garden Query Planner Agent.

    Model 1 performs:
    - Router pattern
    - Planning / Task Decomposition pattern

    The keyword-based method is used as a safe fallback.
    """

    question = state["user_question"].strip()

    if not question:
        state["status"] = "error"
        state["error"] = (
            "The gardening question is empty."
        )
        return state

    try:
        # Main AI routing and planning method.
        return run_ai_planner(state)

    except Exception:
        # Safe keyword-based fallback.
        plant = identify_plant(question)
        question_type = classify_question(question)

        state["plant"] = plant
        state["question_type"] = question_type

        state["search_queries"] = create_search_queries(
            question=question,
            plant=plant,
            question_type=question_type,
        )

        state["plan"] = create_plan(
            plant=plant,
            question_type=question_type,
        )

        state["status"] = "planning_complete"
        state["error"] = None

        return state