from functools import lru_cache

import chromadb
from chromadb.utils.embedding_functions import (
    EmbeddingFunction,
    OllamaEmbeddingFunction,
    OpenAIEmbeddingFunction,
)
from loguru import logger
from pydantic import BaseModel, Field

from valai.config import get_settings
from valai.core.console import console


class AddDocumentArgs(BaseModel):
    """Input model for adding a document to the knowledge base."""

    content: str = Field(
        ..., description="The full text content of the document to add."
    )
    doc_id: str = Field(
        ...,
        description="A unique identifier for the document. A good ID could be a filename or a URL.",
    )


class SearchKnowledgeArgs(BaseModel):
    """Input model for searching the knowledge base."""

    query: str = Field(
        ..., description="The query to search for in the knowledge base."
    )


@lru_cache(maxsize=1)
def get_embedding_function() -> EmbeddingFunction:
    """Creates and returns a compatible embedding function based on application settings.
    This function is cached to ensure only one instance is created.
    """
    settings = get_settings()
    provider = settings.embedding_provider
    console.log(f"Initializing embedding provider: [bold cyan]{provider}[/bold cyan]")

    if provider == "azure":
        if not settings.azure_embedding_model:
            raise ValueError("Azure embedding model name must be configured.")
        return OpenAIEmbeddingFunction(
            api_key=settings.azure_openai_api_key,
            api_base=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
            model_name=settings.azure_embedding_model,
        )
    elif provider == "openai":
        return OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key,
            model_name=settings.openai_embedding_model,
        )
    elif provider == "ollama":
        return OllamaEmbeddingFunction(
            url=settings.ollama_host, model_name=settings.ollama_embedding_model
        )
    else:
        # This case should not be reached due to Pydantic's Literal validation
        raise ValueError(f"Unsupported embedding provider: {provider}")


@lru_cache(maxsize=1)
def get_collection() -> chromadb.Collection:
    """Initializes and returns a cached instance of the ChromaDB collection."""
    client_path = get_settings().chroma_db_path
    if not client_path:
        raise ValueError("The chroma_db_path must be set in the configuration.")

    try:
        client = chromadb.PersistentClient(path=client_path)
        embedding_function = get_embedding_function()
        collection = client.get_or_create_collection(
            name="valai-knowledge-base", embedding_function=embedding_function
        )
        logger.success("ChromaDB collection loaded successfully.")
        return collection
    except Exception as e:
        logger.critical(f"Failed to initialize ChromaDB collection: {e}")
        raise


def add_document_to_knowledge_base(args: AddDocumentArgs) -> str:
    """Learns from a document by adding it to the knowledge base.
    If a document with the same ID already exists, it will be updated.
    """
    try:
        collection = get_collection()
        collection.upsert(documents=[args.content], ids=[args.doc_id])
        logger.info(f"Upserted document with ID '{args.doc_id}' into knowledge base.")
        return f"Document '{args.doc_id}' has been successfully added/updated."
    except Exception as e:
        error_str = str(e).lower()
        if "404" in error_str and "resource not found" in error_str:
            logger.error(f"Embedding model not found (404): {e}")
            return (
                "Error: The embedding model was not found. Please verify your "
                "provider settings in the .env file (e.g., AZURE_OPENAI_ENDPOINT and "
                "AZURE_EMBEDDING_DEPLOYMENT_NAME)."
            )
        logger.opt(exception=True).error(
            f"Unexpected error in add_document_to_knowledge_base: {e}"
        )
        return f"An unexpected error occurred while adding a document: {e}"


def search_knowledge_base(args: SearchKnowledgeArgs) -> str:
    """Searches the knowledge base for information relevant to the user's query."""
    try:
        collection = get_collection()
        results = collection.query(query_texts=[args.query], n_results=3)
        documents = results.get("documents")
        if not documents or not documents[0]:
            return "No relevant information found in the knowledge base."
        return "\n---\n".join(documents[0])
    except Exception as e:
        logger.opt(exception=True).error(
            f"Unexpected error in search_knowledge_base: {e}"
        )
        return f"An unexpected error occurred while searching the knowledge base: {e}"


def get_knowledge_base_stats() -> str:
    """Returns statistics about the knowledge base, such as the number of documents."""
    try:
        collection = get_collection()
        count = collection.count()
        return f"The knowledge base currently contains {count} document(s)."
    except Exception as e:
        logger.opt(exception=True).error(
            f"Unexpected error in get_knowledge_base_stats: {e}"
        )
        return f"An unexpected error occurred: {e}"
