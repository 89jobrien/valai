# ValAI: A Modular, Multi-Agent AI Assistant

ValAI is a sophisticated, command-line-based **AI assistant** built on a powerful multi-agent architecture. It uses a central router to intelligently delegate tasks to a suite of specialized agents, each equipped with unique tools for specific requests. This modular design allows for easy extension and customization, making ValAI a robust platform for building advanced AI applications.

---

## ✨ Core Features

- **Dynamic Agent Routing:** A central router analyzes user queries and dynamically routes them to the most appropriate specialist agent.
- **Modular Agent Architecture:** Each specialist agent (e.g., Search Agent, Code Agent, Calendar Agent) is defined by a simple YAML configuration, making it easy to add, remove, or modify capabilities.
- **Enable/Disable Agents:** A centralized configuration allows you to easily toggle agents on or off without changing the core code.
- **Rich Toolset:** Comes pre-packaged with tools for:
  - Web Search & Browsing
  - Code Execution
  - File System I/O
  - Calendar Management (Google Calendar)
  - Email Sending
  - Note-Taking & To-Do Lists
  - Long-Term Knowledge Base (RAG)
  - System Monitoring
- **Configurable LLM Backends:** Seamlessly switch between local inference with Ollama and powerful cloud models via OpenAI and Azure.
- **Interactive CLI:** A user-friendly command-line interface powered by `rich` for a clean and colorful user experience.

---

## 📂 Project Structure

```ascii
.
├── config/
│   ├── agents/
│   │   ├── calendar_agent.yaml
│   │   ├── code_agent.yaml
│   │   └── ... (other agent configs)
│   └── router.yaml
├── logs/
│   └── valai_assistant.log
├── src/
│   └── valai/
│       ├── agents/
│       │   └── base.py         # Core agent loading and routing logic
│       ├── core/
│       │   ├── assistant.py    # Core asynchronous Assistant class
│       │   ├── config.py       # Pydantic settings management
│       │   ├── console.py      # Shared Rich console instance
│       │   ├── history.py      # Conversation history management
│       │   ├── llm_factory.py  # Creates LLM clients (Ollama/Azure/OpenAI)
│       │   ├── rag_pipeline.py # Background RAG processing
│       │   ├── route.py        # Dynamic Pydantic model for routing
│       │   └── tool_registry.py # Central registry for all tools
│       ├── tools/
│       │   └── ... (all tool modules)
│       ├── app.py              # Main Typer CLI entry point (chooses UI)
│       ├── chainlit_app.py     # Chainlit UI logic
│       └── cli.py              # Command-line interface logic
├── .env.example                # Example environment file
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) - A fast Python package installer and resolver

### 2. Installation

Clone the repository:

```bash
git clone
cd

```

Create a virtual environment:

```bash
uv venv
```

Activate the environment:

```bash
source .venv/bin/activate

```

Install dependencies:

```bash
uv sync
```

### 3. Configuration

Create a `.env` file:

```bash
cp .env.example .env

```

Edit the `.env` file and fill in the required values. At a minimum, configure either the **Ollama** or **Azure OpenAI** settings.

Example .env Configuration

```text
# --- CORE SETTINGS ---

LLM_PROVIDER="ollama"
EMBEDDING_PROVIDER="ollama"

# --- OPENAI SETTINGS (if LLM_PROVIDER="openai") ---
OPENAI_API_KEY="your_openai_key"
OPENAI_LLM_MODEL="gpt-4o"
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"


# --- AZURE OPENAI SETTINGS (if LLM_PROVIDER="azure") ---

AZURE_OPENAI_API_KEY="your_azure_api_key"
AZURE_OPENAI_ENDPOINT="your_azure_endpoint"
AZURE_LLM_DEPLOYMENT_NAME="your_llm_deployment_name"
AZURE_EMBEDDING_DEPLOYMENT_NAME="your_embedding_deployment_name"

# --- OLLAMA SETTINGS (if LLM_PROVIDER="ollama") ---

OLLAMA_HOST="<http://localhost:11434>"
OLLAMA_LLM="llama3"
OLLAMA_EMBEDDING_MODEL="nomic-embed-text"

# --- TOOL API KEYS ---

TAVILY_API_KEY="your_tavily_search_api_key"

# --- EMAIL SETTINGS (for EmailAgent) ---

SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="<your_email@gmail.com>"
SMTP_PASSWORD="your_app_password"

# --- AGENT TOGGLES ---

USE_CALENDAR_AGENT=true
USE_CODE_AGENT=true
USE_EMAIL_AGENT=false
```

**Google Calendar Setup (Optional):**  
To use the Calendar Agent, enable the Google Calendar API and download your `credentials.json`. Follow the [Google Calendar API Python Quickstart](https://developers.google.com/calendar/api/quickstart/python) and place the file in the project root. On first use, you'll be prompted to authenticate in your browser.

### 4. Running the Assistant

Use the main application entry point to launch your desired interface.

- **To run the Chainlit UI (default):**

```bash
uv run start-app
# OR explicitly
uv run start-app --ui chainlit
```

- **To run the CLI:**

```bash
uv run start-app --ui cli
```

---

## 🔧 How It Works

The application operates on a simple but powerful loop:

1. **Input:** User enters a query.
2. **Routing:** The Router Agent analyzes the query and selects the most appropriate specialist from the enabled agents.
3. **Execution:** The Assistant class receives the route and dispatches the query to the chosen agent.
4. **Tool Use:** The specialist agent uses its dedicated tools to fulfill the request.
5. **Output:** The result is streamed back to the user in the CLI.

---

## Extending ValAI: Adding a New Agent

1. **Create the Tool:** Write your tool logic in a new file within `valai/tools/`, using clear docstrings and Pydantic models.
2. **Register the Tool:** Add your function to the `TOOL_REGISTRY` in `valai/core/tool_registry.py`.
3. **Create the Agent YAML:** Add a new `.yaml` file in `config/agents/` (e.g., `new_agent.yaml`), defining its name, system prompt, and tool list.
4. **Add the Agent Toggle:** Add a boolean field to the `AgentToggler` class in `valai/config.py` (e.g., `use_new_agent: bool = True`).

The system will automatically detect the new agent and make it available if its toggle is enabled.

---

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
