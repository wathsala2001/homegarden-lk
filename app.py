import streamlit as st


# Configure the Streamlit browser page.
st.set_page_config(
    page_title="HomeGarden LK",
    page_icon="🌱",
    layout="centered",
)


# Main title.
st.title("🌱 HomeGarden LK")

st.subheader(
    "Agentic AI Home Gardening Assistant for Sri Lankan Households"
)

st.info(
    "Ask questions about planting, watering, fertiliser, soil, "
    "pests, plant diseases, composting and harvesting."
)


# Sidebar information.
st.sidebar.title("About HomeGarden LK")

st.sidebar.write(
    """
    HomeGarden LK searches trusted gardening documents and gives
    clear home-gardening information for Sri Lankan households.
    """
)

st.sidebar.subheader("Three AI Agents")

st.sidebar.write(
    """
    1. Garden Query Planner Agent  
    2. Gardening Knowledge Retrieval Agent  
    3. Gardening Answer and Review Agent
    """
)

st.sidebar.subheader("Four Agentic Patterns")

st.sidebar.write(
    """
    - Router
    - Planning / Task Decomposition
    - ReAct / Tool Use
    - Reflection / Self-checking
    """
)

st.sidebar.subheader("Supported Areas")

st.sidebar.write(
    """
    - Planting
    - Watering
    - Fertiliser
    - Soil preparation
    - Pest control
    - Plant diseases
    - Composting
    - Harvesting
    """
)


# Question section.
st.subheader("Ask a Gardening Question")

question = st.text_area(
    "Enter your home-gardening question:",
    placeholder="Example: How can I grow tomatoes in pots?",
    height=120,
)

st.write("### Example Questions")

st.write(
    """
    - How can I grow tomatoes in pots?
    - What fertiliser is suitable for chilli plants?
    - Why are my brinjal leaves turning yellow?
    - How can I control aphids naturally?
    - How can I prepare compost at home?
    """
)


# Submit button.
if st.button("Ask HomeGarden LK", type="primary"):
    if not question.strip():
        st.warning("Please enter a gardening question.")
    else:
        st.success("The Streamlit interface is working correctly.")

        st.write("### Your Question")

        st.write(question)

        st.info(
            "The gardening RAG knowledge base and the three AI "
            "agents will be connected during the next development stages."
        )


# Safety note.
st.divider()

st.caption(
    "HomeGarden LK provides general gardening information. "
    "Always follow official product labels when using fertilisers "
    "or pesticides."
)