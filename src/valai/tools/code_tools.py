import subprocess
import sys


def run_python_code(code: str) -> str:
    """Executes a given string of Python code and returns its standard output.
    Use this tool to perform calculations, run algorithms, or execute any Python script.
    The code runs in a sandboxed environment. Only use standard Python libraries.

    Args:
        code (str): The Python code to execute.

    Returns:
        The standard output from the executed code, or an error message.

    """
    try:
        # The command is constructed to execute the provided code string
        # `capture_output=True` captures stdout and stderr
        # `text=True` returns stdout and stderr as strings
        # `check=True` raises a CalledProcessError if the command returns a non-zero exit code
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,  # Add a timeout for safety
        )
        output = result.stdout
        if not output:
            return "Code executed successfully with no output."
        return f"Execution successful. Output:\n```\n{output}\n```"
    except subprocess.CalledProcessError as e:
        # This catches errors from within the executed code itself
        return f"Error during execution:\n```\n{e.stderr}\n```"
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out after 30 seconds."
    except Exception as e:
        # This catches other errors, e.g., if the subprocess can't be started
        return f"An unexpected error occurred: {e}"
