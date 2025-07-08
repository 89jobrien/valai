from pathlib import Path

from pydantic import BaseModel, Field


class WriteFileArgs(BaseModel):
    """Input model for the write_file tool."""

    file_path: str = Field(..., description="The relative or absolute path to the file.")
    content: str = Field(..., description="The content to write to the file.")


class ReadFileArgs(BaseModel):
    """Input model for the read_file tool."""

    file_path: str = Field(..., description="The relative or absolute path to the file.")


def write_file(args: WriteFileArgs) -> str:
    """Writes content to a specified file, creating directories if they don't exist.
    Use this tool to save text, such as code, reports, or summaries, to a file.
    """
    try:
        path = Path(args.file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(args.content)
        return f"Successfully wrote content to '{args.file_path}'."
    except Exception as e:
        return f"Error writing to file '{args.file_path}': {e}"


def read_file(args: ReadFileArgs) -> str:
    """Reads the content of a specified file.
    Use this tool to retrieve the contents of a file for analysis, summarization, or modification.
    """
    try:
        path = Path(args.file_path)
        if not path.is_file():
            return f"Error: File not found at '{args.file_path}'."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{args.file_path}': {e}"
