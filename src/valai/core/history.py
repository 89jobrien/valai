# valai/core/history.py

from pydantic_ai import RunContext
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)


def context_aware_processor(
    ctx: RunContext[None],
    messages: list[ModelMessage],
) -> list[ModelMessage]:
    """An example history processor that truncates the message history
    if the token count exceeds a certain threshold.
    """
    # Access current usage
    current_tokens = ctx.usage.total_tokens

    # Filter messages based on context
    if current_tokens > 1000:  # type: ignore
        return messages[-3:]  # Keep only recent messages when token usage is high
    return messages


class ConversationHistory:
    """Manages the history of a conversation for pydantic-ai agents."""

    def __init__(self, capacity: int = 10):
        """Initializes the conversation history.

        Args:
            capacity: The maximum number of messages to store.

        """
        self._messages: list[ModelMessage] = []
        self.capacity = capacity

    def add(self, role: str, content: str):
        """Adds a message to the history, creating the appropriate
        pydantic-ai message type based on the role.

        Args:
            role: The role of the message sender (e.g., 'user', 'assistant').
            content: The text content of the message.

        """
        if len(self._messages) >= self.capacity:
            self._messages.pop(0)  # Remove the oldest message to maintain capacity

        if role == "user":
            message = ModelRequest(
                parts=[UserPromptPart(content=content)]
            )  # Correctly using UserPromptPart
        elif role == "assistant":
            message = ModelResponse(
                parts=[TextPart(content=content)]
            )  # Correctly using TextPart
        else:
            raise ValueError(f"Unhandled message role: {role}")

        self._messages.append(message)

    @property
    def messages(self) -> list[ModelMessage]:
        """Returns the history as a list of pydantic-ai ModelMessage objects."""
        return self._messages
