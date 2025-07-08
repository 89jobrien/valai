# ValAI: A Modular, Multi-Agent AI Assistant

ValAI is a sophisticated, command-line-based **AI assistant** built on a powerful multi-agent architecture. It uses a central Router to intelligently delegate tasks to a suite of specialized agents, each equipped with unique tools for specific requests. This modular design allows for easy extension and customization, making ValAI a robust platform for building advanced AI applications.

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
