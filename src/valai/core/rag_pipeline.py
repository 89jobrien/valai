import threading

from loguru import logger
from pydantic_ai.messages import TextPart, UserPromptPart
from valai.core.history import ConversationHistory
from valai.tools.knowledge_tools import (
    AddDocumentArgs,
    add_document_to_knowledge_base,
    get_collection,
)


class BackgroundRAG:
    """Manages a background pipeline to process and embed conversations
    into the knowledge base, creating a continuous learning loop.
    """

    def __init__(self):
        """Initializes the RAG pipeline with a database collection."""
        try:
            # Eagerly initialize the collection to catch errors at startup
            self.collection = get_collection()
            logger.info("Background RAG pipeline initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            self.collection = None

    def _process_and_embed(self, conversation_history: ConversationHistory):
        """The target function for the background thread. It formats the
        last turn of a conversation and embeds it into the knowledge base.
        """
        if not self.collection:
            logger.warning(
                "RAG pipeline is not available. Skipping conversation embedding."
            )
            return

        try:
            # Get the last two messages (user query and assistant response)
            last_turn = conversation_history.messages[-2:]
            if len(last_turn) < 2:
                return  # Not a full turn, nothing to embed

            user_msg = last_turn[0].parts[0].content if isinstance(last_turn[0].parts[0], UserPromptPart) else None
            assistant_msg = last_turn[1].parts[0].content if isinstance(last_turn[1].parts[0], TextPart) else None

            # Format the conversation turn into a single document
            document_content = (
                f"User Question: {user_msg}\n\nAssistant's Answer: {assistant_msg}"
            )

            # Use a hash of the content for a deterministic ID
            doc_id = f"conv_{hash(document_content)}"

            logger.info(
                f"Embedding conversation turn (ID: {doc_id}) into knowledge base."
            )
            # Use the existing tool function to add the document
            add_document_to_knowledge_base(
                args=AddDocumentArgs(content=document_content, doc_id=doc_id)
            )
        except Exception as e:
            logger.error(f"Error in background RAG processing thread: {e}")

    def run_in_background(self, conversation_history: ConversationHistory):
        """Starts the embedding process in a non-blocking background thread."""
        history_copy = conversation_history

        thread = threading.Thread(target=self._process_and_embed, args=(history_copy,))
        thread.daemon = True
        thread.start()

        logger.info("Background RAG processing thread started.")
