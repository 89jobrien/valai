import json
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Optional

from loguru import logger
from pydantic import BaseModel, Field

TODO_FILE = Path("todo_list.json")


class TodoItem(BaseModel):
    """Data model for a single to-do item."""

    id: int
    task: str
    status: Literal["pending", "completed"] = "pending"
    created_at: datetime
    completed_at: Optional[datetime] = None


class AddTodoArgs(BaseModel):
    """Input model for the add_todo tool."""

    task: str = Field(..., description="A clear and concise description of the task.")


class CompleteTodoArgs(BaseModel):
    """Input model for the complete_todo tool."""

    task_id: int = Field(..., description="The unique ID of the task to mark as complete.")


def _load_todos() -> List[TodoItem]:
    """Loads the to-do list from the JSON file."""
    if not TODO_FILE.exists():
        return []
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [TodoItem(**item) for item in data]
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading to-do file: {e}")
        return []


def _save_todos(todos: List[TodoItem]):
    """Saves the to-do list to the JSON file."""
    try:
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            data = [item.model_dump(mode="json") for item in todos]
            json.dump(data, f, indent=4)
    except IOError as e:
        logger.error(f"Error saving to-do file: {e}")


def add_todo(args: AddTodoArgs) -> str:
    """Adds a new task to the to-do list."""
    todos = _load_todos()
    new_id = (max(item.id for item in todos) + 1) if todos else 1
    new_item = TodoItem(id=new_id, task=args.task, created_at=datetime.now())
    todos.append(new_item)
    _save_todos(todos)
    logger.info(f"Added new to-do item #{new_id}: '{args.task}'")
    return f"✅ To-do item added: '{args.task}' (ID: {new_id})."


def view_todos() -> str:
    """Displays all current to-do items, separated by status."""
    todos = _load_todos()
    if not todos:
        return "Your to-do list is empty! ✨"

    pending = [item for item in todos if item.status == "pending"]
    completed = [item for item in todos if item.status == "completed"]

    response = ""
    if pending:
        response += "📋 Pending Tasks:\n"
        response += "\n".join([f"  - ID {item.id}: {item.task}" for item in pending])
    else:
        response += "👍 No pending tasks!"

    if completed:
        response += "\n\n✅ Completed Tasks:\n"
        response += "\n".join([f"  - ID {item.id}: {item.task}" for item in completed])

    return response


def complete_todo(args: CompleteTodoArgs) -> str:
    """Marks a specific to-do item as complete by its ID."""
    todos = _load_todos()
    task_to_complete = next((item for item in todos if item.id == args.task_id), None)

    if not task_to_complete:
        return f"❌ Error: To-do item with ID {args.task_id} not found."

    if task_to_complete.status == "completed":
        return f"👍 Task ID {args.task_id} is already marked as complete."

    task_to_complete.status = "completed"
    task_to_complete.completed_at = datetime.now()
    _save_todos(todos)
    logger.info(f"Completed to-do item #{args.task_id}: '{task_to_complete.task}'")
    return f"🎉 Great job! Task ID {args.task_id} ('{task_to_complete.task}') has been marked as complete."
