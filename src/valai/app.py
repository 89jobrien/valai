import subprocess
import sys

import typer
from loguru import logger
from typing_extensions import Annotated

cli_app = typer.Typer()


@cli_app.command()
def run(
    ui: Annotated[
        str,
        typer.Option(
            "--ui",
            "-u",
            help="The user interface to run: 'cli' or 'chainlit'.",
        ),
    ] = "chainlit",
):
    """Run the ValAI assistant with the specified user interface."""
    if ui.lower() == "cli":
        logger.info("Starting ValAI in CLI mode...")
        try:
            subprocess.run([sys.executable, "-m", "valai.cli"], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start CLI: {e}")
            sys.exit(1)

    elif ui.lower() == "chainlit":
        logger.info("Starting ValAI in Chainlit mode...")
        try:
            subprocess.run(
                ["chainlit", "run", "src/valai/chainlit_app.py", "-w"], check=True
            )
        except FileNotFoundError:
            logger.error(
                "Could not find the 'chainlit' command. Please ensure Chainlit is installed and in your PATH."
            )
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start Chainlit UI: {e}")
            sys.exit(1)
    else:
        logger.error(f"Invalid UI option: '{ui}'. Please choose 'cli' or 'chainlit'.")
        sys.exit(1)


if __name__ == "__main__":
    cli_app()
