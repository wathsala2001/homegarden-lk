from typing import Dict, List

from core.state import GardenState


# Plants currently supported by HomeGarden LK.
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


def identify_plant(question: str) -> str:
    """
    Identify the plant mentioned in the user's question.
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
    """

    question_lower = question.lower()

    # Check disease and pest categories before general planting.
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
    Create search phrases for the gardening knowledge base.
    """

    queries = [question.strip()]

    if plant != "unknown":
        queries.append(f"{plant} {question_type.replace('_', ' ')}")
        queries.append(
            f"{plant} home gardening {question_type.replace('_', ' ')}"
        )
    else:
        queries.append(
            f"home gardening {question_type.replace('_', ' ')}"
        )

    # Remove duplicate queries while keeping the original order.
    return list(dict.fromkeys(queries))


def create_plan(
    plant: str,
    question_type: str,
) -> List[str]:
    """
    Planning pattern:
    Divide the question-answering process into smaller tasks.
    """

    plant_name = plant if plant != "unknown" else "the plant"
    readable_type = question_type.replace("_", " ")

    return [
        f"Identify information about {plant_name}.",
        f"Search documents about {readable_type}.",
        "Retrieve the most relevant gardening evidence.",
        "Prepare clear actions supported by the documents.",
    ]


def run_query_planner(state: GardenState) -> GardenState:
    """
    Run Agent 1: Garden Query Planner Agent.

    The agent updates and returns the shared structured state.
    """

    question = state["user_question"].strip()

    if not question:
        state["status"] = "error"
        state["error"] = "The gardening question is empty."
        return state

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