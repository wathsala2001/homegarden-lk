# HomeGarden LK

## Agentic AI Home Gardening Assistant for Sri Lankan Households

**Student Name:** Wathsala Kithulgala  
**Index Number:** ITBIN-2312-0025  
**Module:** IT41043 – Intelligent Systems (Agentic AI)  
**GitHub Repository:** https://github.com/wathsala2001/homegarden-lk  
**Retrieval Success Rate:** 80.0%

---

## 1. Project Introduction

HomeGarden LK is an Agentic AI home-gardening assistant developed for Sri Lankan households.

The system helps users ask questions about common gardening topics such as:

- Plant watering
- Fertiliser use
- Compost preparation
- Pest control
- Plant diseases
- Vegetable cultivation

The system does not only depend on the general knowledge of an AI model. It retrieves information from a collection of gardening documents before preparing the answer.

---

## 2. Main Objective

The main objective of this project is to develop an Agentic AI system that can provide useful and document-supported home-gardening guidance.

The system uses multiple agents, different AI models and a Retrieval-Augmented Generation process.

---

## 3. Target Users

The main users of HomeGarden LK are:

- Sri Lankan home gardeners
- Beginner gardeners
- People growing vegetables in small gardens
- People growing plants in containers
- Households looking for simple gardening guidance

---

## 4. Main Features

HomeGarden LK includes:

- Three communicating AI agents
- Three different AI model roles
- Four agentic design patterns
- Structured JSON communication
- RAG using more than 20 gardening documents
- Semantic document retrieval
- AI-based evidence ranking
- Answer checking and revision
- Source-supported responses
- Streamlit user interface
- Retrieval evaluation

---

## 5. AI Agents

### Agent 1 – Query Planner Agent

The Query Planner Agent receives the user’s question.

It identifies the question category and prepares a search plan. It also creates suitable search queries for the Retrieval Agent.

Example categories include watering, fertiliser, pests, diseases and cultivation.

### Agent 2 – Retrieval Agent

The Retrieval Agent searches the gardening knowledge base.

It retrieves related document chunks and uses an AI model to rank them according to their relevance to the user’s question.

### Agent 3 – Answer and Review Agent

The Answer and Review Agent prepares the final answer using the retrieved evidence.

It also checks whether the answer is supported by the documents. When the answer is incomplete or unsupported, the agent can revise it.

---

## 6. AI Models

The project uses three model roles:

| Model Role | Model | Main Task |
|---|---|---|
| Router and Planner | `llama-3.1-8b-instant` | Understand the question and prepare a plan |
| Evidence Ranker | `openai/gpt-oss-20b` | Rank retrieved gardening information |
| Final Answer Model | `openai/gpt-oss-120b` | Generate and review the final answer |

Each model is assigned a different task in the system.

---

## 7. Agentic AI Patterns

The project uses four Agentic AI patterns.

### 1. Routing

The system identifies the type of gardening question and sends it through the correct workflow.

### 2. Planning

The Query Planner Agent creates a plan and search queries before document retrieval begins.

### 3. ReAct

The system performs actions such as document searching and observes the retrieved results before continuing.

### 4. Reflection

The Answer and Review Agent checks whether the generated answer is supported by the retrieved documents. It revises the answer when required.

---

## 8. RAG Knowledge Base

The project uses Retrieval-Augmented Generation.

The knowledge base contains more than 20 gardening PDF documents. The documents cover home-gardening topics such as vegetable cultivation, compost, pests, fertiliser, watering and plant diseases.

The main RAG process is:

1. Load the PDF documents.
2. Extract the text.
3. Divide the text into smaller chunks.
4. Create embeddings using FastEmbed.
5. Store the embeddings in a NumPy vector store.
6. Convert the user’s question into an embedding.
7. Find the most similar document chunks.
8. Rank the retrieved evidence.
9. Generate an answer using the evidence.

---

## 9. Structured Agent Communication

The agents communicate using a structured shared state.

The shared state contains information such as:

```json
{
  "user_question": "How often should I water tomato plants?",
  "category": "watering",
  "search_queries": [
    "tomato plant watering frequency",
    "watering tomato plants in home gardens"
  ],
  "retrieved_documents": [],
  "ranked_evidence": [],
  "final_answer": "",
  "sources": [],
  "status": "processing",
  "error": null
}
```

Structured messages help the agents share information clearly and reduce communication errors.

---

## 10. System Architecture

The system architecture diagram is available here:

[View System Architecture](diagrams/system_architecture.md)

The main workflow is:

```text
User
  ↓
Streamlit Interface
  ↓
Query Planner Agent
  ↓
Retrieval Agent
  ↓
RAG Knowledge Base
  ↓
Answer and Review Agent
  ↓
Final Answer with Sources
```

---

## 11. Agent Communication

The agent communication diagram is available here:

[View Agent Communication Diagram](diagrams/agent_communication.md)

The agents communicate in the following order:

1. The user submits a gardening question.
2. The Query Planner Agent identifies the category.
3. The Query Planner Agent prepares search queries.
4. The Retrieval Agent searches the knowledge base.
5. The Retrieval Agent ranks the retrieved evidence.
6. The Answer and Review Agent generates the answer.
7. The answer is checked and revised when required.
8. The final answer and sources are shown to the user.

---

## 12. Retrieval Evaluation

I tested the retrieval system using five sample gardening questions.

The questions covered topics such as:

- Tomato watering
- Chilli fertiliser
- Compost preparation
- Natural pest control
- Brinjal leaf problems

Four out of the five questions retrieved relevant gardening information.

**Retrieval Success Rate: 80.0%**

This result shows that the knowledge base can retrieve useful information for most common home-gardening questions. However, retrieval can still be improved for questions that use unclear or different wording.

Detailed results are available in:

- `evaluation/retrieval_results.csv`
- `evaluation/retrieval_summary.md`

---

## 13. Technologies Used

- Python
- Streamlit
- Groq API
- FastEmbed
- NumPy
- PyPDF
- Pandas
- JSON
- Git
- GitHub
- Visual Studio Code

---

## 14. Project Folder Structure

```text
homegarden-lk/
│
├── agents/
│   ├── query_planner_agent.py
│   ├── retrieval_agent.py
│   └── answer_review_agent.py
│
├── core/
│   └── orchestrator.py
│
├── data/
│   ├── raw_documents/
│   └── vector_store/
│
├── diagrams/
│   ├── system_architecture.md
│   └── agent_communication.md
│
├── evaluation/
│   ├── retrieval_questions.json
│   ├── evaluate_retrieval.py
│   ├── retrieval_results.csv
│   └── retrieval_summary.md
│
├── models/
│   └── model_manager.py
│
├── rag/
│   ├── document_loader.py
│   ├── text_chunker.py
│   ├── embedding_manager.py
│   ├── vector_store.py
│   └── retriever.py
│
├── scripts/
│   └── build_index.py
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 15. Installation

### Step 1 – Clone the repository

```bash
git clone https://github.com/wathsala2001/homegarden-lk.git
cd homegarden-lk
```

### Step 2 – Create a virtual environment

```bash
python -m venv venv
```

### Step 3 – Activate the virtual environment

For Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### Step 4 – Install the required libraries

```bash
pip install -r requirements.txt
```

### Step 5 – Create the environment file

Create a file named `.env` and add:

```env
GROQ_API_KEY=your_groq_api_key
ROUTER_MODEL=llama-3.1-8b-instant
RERANK_MODEL=openai/gpt-oss-20b
FINAL_MODEL=openai/gpt-oss-120b
```

The real API key should not be uploaded to GitHub.

### Step 6 – Build the vector index

```bash
python scripts/build_index.py
```

### Step 7 – Run the application

```bash
python -m streamlit run app.py
```

---

## 16. Example Question

```text
How often should I water tomato plants?
```

The system plans the search, retrieves relevant document information, ranks the evidence and generates an answer with sources.

---

## 17. Challenges I Faced

During the project, I faced several challenges.

One challenge was connecting three agents and passing information between them. I solved this by using a structured shared state.

I also faced difficulties when creating and loading the vector store. I tested each RAG component separately before connecting it to the full agent workflow.

Another challenge was ensuring that the generated answer was supported by the retrieved documents. I added a review and reflection process to check the answer before showing it to the user.

---

## 18. What I Learned

Through this project, I learned:

- How Agentic AI systems work
- How different agents communicate
- How to assign different tasks to different AI models
- How RAG retrieves information from documents
- How embeddings and vector similarity work
- How reflection can improve an AI-generated answer
- How to use Git branches and Pull Requests
- How to develop a Streamlit interface

---

## 19. Limitations

The current system has several limitations:

- It mainly supports home-gardening questions.
- The answer quality depends on the available documents.
- Some questions may retrieve partly relevant documents.
- An internet connection is required to access the AI models.
- The system does not replace professional agricultural advice.
- The current retrieval success rate is 80.0%, so retrieval can still be improved.

---

## 20. Future Improvements

The project can be improved by:

- Adding more Sri Lankan gardening documents
- Supporting Sinhala and Tamil questions
- Adding weather-based recommendations
- Improving document metadata
- Increasing the number of evaluation questions
- Improving retrieval for unclear questions
- Adding image-based plant disease identification

---

## 21. Conclusion

HomeGarden LK is an Agentic AI home-gardening assistant developed for Sri Lankan households.

The system successfully combines three AI agents, three model roles, four agentic patterns, structured communication and a RAG knowledge base. It can retrieve gardening information, generate source-supported answers and review its own output before presenting the final response.

The project helped me understand how a complete Agentic AI system can be designed, built, tested and deployed.