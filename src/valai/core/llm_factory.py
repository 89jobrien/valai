from chromadb.utils.embedding_functions import (
    OllamaEmbeddingFunction,
    OpenAIEmbeddingFunction,
)
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.azure import AzureProvider
from pydantic_ai.providers.openai import OpenAIProvider

from valai.config import get_settings


def get_llm_client() -> OpenAIModel:
    """Factory to get the configured LLM client for pydantic-ai."""
    settings = get_settings()
    if settings.llm_provider == "azure":
        return OpenAIModel(
            model_name=str(settings.azure_llm),
            provider=AzureProvider(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            ),
        )
    elif settings.llm_provider == "openai":
        return OpenAIModel(
            model_name=settings.openai_llm_model,
            provider=OpenAIProvider(api_key=settings.openai_api_key),
        )
    else:
        return OpenAIModel(
            model_name=settings.ollama_llm_model,
            provider=OpenAIProvider(base_url=settings.ollama_host),
        )


def get_embedding_client():
    """Factory to get the configured embedding client."""
    settings = get_settings()
    if settings.embedding_provider == "azure":
        return OpenAIEmbeddingFunction(
            api_key=settings.azure_openai_api_key,
            api_base=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
            model_name=str(settings.azure_embedding_model),
        )
    elif settings.embedding_provider == "openai":
        return OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key,
            model_name=settings.openai_embedding_model,
        )
    return OllamaEmbeddingFunction(
        url=settings.ollama_host, model_name=settings.ollama_embedding_model
    )
