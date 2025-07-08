from pydantic import BaseModel, Field
from pydantic_ai import Agent

from valai.core.llm_factory import get_llm_client


class BaseTextArgs(BaseModel):
    """Base model for text input."""

    text: str = Field(..., description="The text to be processed.")


class ChangeToneArgs(BaseModel):
    """Input model for the change_tone tool."""

    text: str = Field(..., description="The text to be processed.")
    tone: str = Field(
        ...,
        description="The desired tone (e.g., Formal, Casual, Confident, Friendly).",
    )


async def _run_writing_task(prompt: str, text: str) -> str:
    """Helper function to run a writing task with a given prompt."""
    agent = Agent(model=get_llm_client(), system_prompt=prompt)
    result = await agent.run(user_prompt=text)
    return str(result)


async def improve_writing(args: BaseTextArgs) -> str:
    """Improves the provided text, focusing on clarity, engagement, and flow."""
    prompt = "You are a writing assistant. Improve the following text, focusing on clarity, engagement, and flow. Do not just fix grammar and spelling. Only output the improved text."
    return await _run_writing_task(prompt, args.text)


async def fix_spelling_grammar(args: BaseTextArgs) -> str:
    """Fixes all spelling and grammar mistakes in the provided text."""
    prompt = "You are a writing assistant. Fix all spelling and grammar mistakes in the following text. Only output the corrected text."
    return await _run_writing_task(prompt, args.text)


async def make_shorter(args: BaseTextArgs) -> str:
    """Makes the provided text shorter and more concise."""
    prompt = "You are a writing assistant. Make the following text shorter and more concise. Only output the shortened text."
    return await _run_writing_task(prompt, args.text)


async def make_longer(args: BaseTextArgs) -> str:
    """Expands on the provided text, adding more detail and explanation."""
    prompt = "You are a writing assistant. Expand on the following text, adding more detail and explanation. Only output the expanded text."
    return await _run_writing_task(prompt, args.text)


async def change_tone(args: ChangeToneArgs) -> str:
    """Rewrites the provided text in a specified tone."""
    prompt = f"You are a writing assistant. Rewrite the following text in a {args.tone.lower()} tone. Only output the rewritten text."
    return await _run_writing_task(prompt, args.text)
