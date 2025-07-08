import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class AgentToggler(BaseSettings):
    """Defines which specialist agents are enabled.
    Reads settings from environment variables (e.g., USE_CODE_AGENT=false).
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    use_generalist_agent: bool = True
    use_calendar_agent: bool = True
    use_code_agent: bool = True
    use_email_agent: bool = True
    use_file_agent: bool = True
    # use_knowledge_agent: bool = True
    use_note_agent: bool = True
    use_search_agent: bool = True
    use_system_agent: bool = True
    use_webscraping_agent: bool = True
    use_todo_agent: bool = True
    use_writing_agent: bool = True


class Settings(BaseSettings):
    """Manages application settings using Pydantic."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Provider Configuration ---
    llm_provider: Literal["azure", "ollama", "openai"] = "openai"
    embedding_provider: Literal["azure", "ollama", "openai"] = "ollama"

    # --- OpenAI Settings ---
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_llm_model: str = os.getenv("OPENAI_LLM_MODEL", "gpt-4o")
    openai_embedding_model: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )

    # --- Azure OpenAI Settings ---
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    azure_llm: str = os.getenv("AZURE_LLM_DEPLOYMENT_NAME", "")
    azure_embedding_model: str = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME", "")

    # --- Ollama Settings ---
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_llm_model: str = os.getenv("OLLAMA_LLM", "llama3")
    ollama_embedding_model: str = os.getenv(
        "OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"
    )

    # --- Tool API Keys ---
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

    # --- Vector Store ---
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./db/chroma_db")

    # --- Email Server Settings ---
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", 587))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")

    # --- Agent Toggles ---
    # This nested model holds the on/off switches for each agent.
    # You can override these in your .env file, e.g., USE_CODE_AGENT=False
    agent_toggler: AgentToggler = AgentToggler()


@lru_cache
def get_settings() -> Settings:
    """Returns a cached instance of the application settings."""
    return Settings()
