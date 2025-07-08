import json
from datetime import datetime
from pathlib import Path
from typing import List

from loguru import logger
from pydantic import BaseModel, Field

NOTES_FILE = Path("notes.json")


class Note(BaseModel):
    """Data model for a single note."""

    id: int
    title: str
    content: str
    created_at: datetime


class SaveNoteArgs(BaseModel):
    """Input model for the save_note tool."""

    title: str = Field(..., description="A concise title for the note.")
    content: str = Field(..., description="The full content of the note.")


class SearchNotesArgs(BaseModel):
    """Input model for the search_notes tool."""

    query: str = Field(
        ..., description="The text to search for in note titles and content."
    )


class DeleteNoteArgs(BaseModel):
    """Input model for the delete_note tool."""

    note_id: int = Field(..., description="The unique ID of the note to delete.")


def _load_notes() -> List[Note]:
    """Loads notes from the JSON file."""
    if not NOTES_FILE.exists():
        return []
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes_data = json.load(f)
            return [Note(**note) for note in notes_data]
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading notes file: {e}")
        return []


def _save_notes(notes: List[Note]):
    """Saves a list of notes to the JSON file."""
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            notes_data = [note.model_dump(mode="json") for note in notes]
            json.dump(notes_data, f, indent=4)
    except IOError as e:
        logger.error(f"Error saving notes file: {e}")


def save_note(args: SaveNoteArgs) -> str:
    """Use this tool to save a new note."""
    notes = _load_notes()
    new_id = (max(note.id for note in notes) + 1) if notes else 1
    new_note = Note(
        id=new_id,
        title=args.title,
        content=args.content,
        created_at=datetime.now(),
    )
    notes.append(new_note)
    _save_notes(notes)
    return f"Note '{args.title}' (ID: {new_id}) saved successfully."


def retrieve_notes() -> str:
    """Use this tool to retrieve a summary of all previously saved notes."""
    notes = _load_notes()
    if not notes:
        return "No notes found."
    summaries = [
        f"- ID {note.id}: {note.title} (Created: {note.created_at.strftime('%Y-%m-%d %H:%M')})"
        for note in notes
    ]
    return "Here are your notes:\n" + "\n".join(summaries)


def search_notes(args: SearchNotesArgs) -> str:
    """Searches for notes containing the query text in their title or content."""
    notes = _load_notes()
    if not notes:
        return "No notes to search."

    query_lower = args.query.lower()
    found_notes = [
        note
        for note in notes
        if query_lower in note.title.lower() or query_lower in note.content.lower()
    ]

    if not found_notes:
        return f"No notes found matching '{args.query}'."

    results = [f"ID {note.id}: {note.title}\n{note.content}" for note in found_notes]
    return "Found matching notes:\n\n" + "\n---\n".join(results)


def delete_note(args: DeleteNoteArgs) -> str:
    """Deletes a specific note by its ID."""
    notes = _load_notes()
    note_to_delete = next((note for note in notes if note.id == args.note_id), None)

    if not note_to_delete:
        return f"Error: Note with ID {args.note_id} not found."

    notes.remove(note_to_delete)
    _save_notes(notes)
    return f"Successfully deleted note ID {args.note_id} ('{note_to_delete.title}')."
