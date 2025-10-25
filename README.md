# 🤖 App Builder

**App Builder** is an AI-powered coding assistant built with **LangGraph** that functions like a multi-agent developer team.  
It can take a natural language request and generate a **complete, working project** — file by file — using real developer workflows.

---

## 🧠 Architecture

App Builder consists of three main agents working together in a **state-based graph**:

- **Planner Agent** – Analyzes user input and creates a structured project plan.  
- **Architect Agent** – Breaks down the plan into detailed engineering tasks for each file.  
- **Coder Agent** – Implements each task using tools like a real developer (reads, writes, and manages files).

Each agent communicates through a **shared state** that keeps updating as the workflow progresses.

---

## 🏗️ How It Works

The system uses **LangGraph** to connect agents through a directed graph:

1. **Planner ➜ Architect ➜ Coder**  
2. The **Planner** creates a project plan.  
3. The **Architect** converts the plan into step-by-step tasks.  
4. The **Coder** executes each step — reading, writing, and updating files until the project is complete.  
5. The process ends automatically when all tasks are done.

---

## ⚙️ Key Components Explained

- `Field`: Decorator for model attributes, allows setting defaults, validations, and docs.  
- `END`: Special marker indicating the end of the LangGraph workflow.  
- `StateGraph`: Core class used to build and manage the state-based execution graph.  
- `set_debug(True)`: Enables detailed debugging info for LangChain execution.  
- `set_verbose(True)`: Enables step-by-step logs of LangChain flow.

---

## 🚀 Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) installed (for virtual environment management).  
- A **Groq account** and API key — get one [here](https://console.groq.com/keys).

### Installation & Setup

```bash
# 1. Create a virtual environment
uv venv
source .venv/bin/activate

# 2. Install dependencies
uv pip install -r pyproject.toml

# 3. Configure environment variables
cp .sample_env .env
# Edit .env and add your Groq API key

# 4. Run the app
python main.py
