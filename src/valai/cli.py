import asyncio
import sys

from valai.core.assistant import Assistant
from valai.core.console import console


async def cli_main_loop():
    valai = Assistant()
    console.print("\n🗣️ You can now chat with ValAI. Type 'exit' to quit.")
    loop = asyncio.get_running_loop()

    while True:
        try:
            user_query = await loop.run_in_executor(None, lambda: input("You: "))

            if user_query.lower() in ["exit", "quit"]:
                break

            console.print("\nValAI: ", end="")
            final_response = ""
            async for chunk in valai.process_query(user_query):
                if "status" in chunk:
                    # using a dim style to differentiate them from the final answer.
                    console.log(f"[dim]{chunk['status']}[/dim]")
                elif "final_answer" in chunk:
                    final_response = chunk["final_answer"]
            console.print(f"{final_response}\n")

        except (KeyboardInterrupt, EOFError):
            # Gracefully handle Ctrl+C or end-of-file (Ctrl+D).
            break

    console.print("👋 Goodbye!")


def start_cli():
    """Synchronous entry point that initializes and runs the async CLI main loop."""
    try:
        asyncio.run(cli_main_loop())
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!")
    finally:
        sys.exit(0)


if __name__ == "__main__":
    start_cli()
