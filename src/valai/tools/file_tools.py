import shutil
from pathlib import Path

from pydantic import BaseModel, Field


class WriteFileArgs(BaseModel):
    """Input model for the write_file tool."""

    file_path: str = Field(
        ..., description="The relative or absolute path to the file."
    )
    content: str = Field(..., description="The content to write to the file.")


class ReadFileArgs(BaseModel):
    """Input model for the read_file tool."""

    file_path: str = Field(
        ..., description="The relative or absolute path to the file."
    )


class ListDirectoryArgs(BaseModel):
    """Input model for the list_directory tool."""

    path: str = Field(
        default=".",
        description="The path of the directory to list. Defaults to the current directory.",
    )


class CreateDirectoryArgs(BaseModel):
    """Input model for the create_directory tool."""

    path: str = Field(..., description="The path of the directory to create.")


class DeleteArgs(BaseModel):
    """Input model for the delete_file_or_directory tool."""

    path: str = Field(..., description="The path of the file or directory to delete.")


def write_file(args: WriteFileArgs) -> str:
    """Writes content to a specified file, creating directories if they don't exist."""
    try:
        path = Path(args.file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(args.content)
        return f"Successfully wrote content to '{args.file_path}'."
    except Exception as e:
        return f"Error writing to file '{args.file_path}': {e}"


def read_file(args: ReadFileArgs) -> str:
    """Reads the content of a specified file."""
    try:
        path = Path(args.file_path)
        if not path.is_file():
            return f"Error: File not found at '{args.file_path}'."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{args.file_path}': {e}"


def list_directory(args: ListDirectoryArgs) -> str:
    """Lists the contents of a specified directory."""
    try:
        path = Path(args.path)
        if not path.is_dir():
            return f"Error: '{args.path}' is not a valid directory."
        items = [f.name for f in path.iterdir()]
        if not items:
            return f"The directory '{args.path}' is empty."
        return "Directory listing:\n- " + "\n- ".join(items)
    except Exception as e:
        return f"Error listing directory '{args.path}': {e}"


def create_directory(args: CreateDirectoryArgs) -> str:
    """Creates a new directory at the specified path."""
    try:
        path = Path(args.path)
        path.mkdir(parents=True, exist_ok=True)
        return f"Successfully created directory at '{args.path}'."
    except Exception as e:
        return f"Error creating directory '{args.path}': {e}"


def delete_file_or_directory(args: DeleteArgs) -> str:
    """Deletes a file or an entire directory tree. Use with extreme caution."""
    try:
        path = Path(args.path)
        if not path.exists():
            return f"Error: Path '{args.path}' does not exist."

        if path.is_file():
            path.unlink()
            return f"Successfully deleted file: '{args.path}'"
        elif path.is_dir():
            shutil.rmtree(path)
            return f"Successfully deleted directory and all its contents: '{args.path}'"
        else:
            return f"Error: Path '{args.path}' is neither a file nor a directory."
    except Exception as e:
        return f"Error deleting '{args.path}': {e}"
