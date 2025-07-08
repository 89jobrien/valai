# valai/main.py

import sys
from typing import Dict

from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult

from valai.agents.base import Route, load_agents, load_router
from valai.core.console import console
from valai.core.history import ConversationHistory

# from valai.core.rag.rag_pipeline import BackgroundRAG


class Assistant:
    """Orchestrates the agent routing and execution logic."""

    def __init__(self):
        """Initializes the assistant and all its components."""
        logger.add(
            "logs/valai_assistant.log",
            rotation="10 MB",
            level="INFO",
            backtrace=True,
            diagnose=True,
        )
        console.print("🚀 Initializing ValAI Assistant...")

        self.router: Agent = load_router()
        self.specialists: Dict[str, Agent] = load_agents()
        self.history = ConversationHistory()
        # self.rag_pipeline = BackgroundRAG()

        console.print("✅ Assistant is ready.")

    def _get_routing_decision(self, query: str) -> Route:  # type: ignore
        """Routes the user's query to the appropriate specialist."""
        console.print("\n🧠 Thinking... (Routing query)")
        # ... (rest of the function is unchanged)
        raw_result = self.router.run_sync(
            user_prompt=query,
            message_history=self.history.messages,
            output_type=Route,  # type: ignore
        )

        if isinstance(raw_result, AgentRunResult):
            route = raw_result.output
        elif isinstance(raw_result, dict) and "output" in raw_result:
            route = Route.model_validate(raw_result["output"])
        elif isinstance(raw_result, Route):  # type: ignore
            route = raw_result
        else:
            raise TypeError(f"Unexpected output type from router: {type(raw_result)}")

        if not isinstance(route, Route):  # type: ignore
            raise TypeError(
                f"Extracted output is not a valid Route object: {type(route)}"
            )

        console.print(f"🚦 Routing to: {route.specialist_name}")  # type: ignore
        return route

    def _execute_specialist_task(self, route: Route) -> str:  # type: ignore
        """Executes the task using the chosen specialist."""
        # ... (this function is unchanged)
        specialist_name = route.specialist_name
        specialist_query = route.query_for_specialist

        if specialist_name not in self.specialists:
            return f"Error: Could not find specialist '{specialist_name}'."

        specialist = self.specialists[specialist_name]
        console.print(f"🛠️ Specialist '{specialist_name}' is working...")

        try:
            result = specialist.run_sync(
                user_prompt=specialist_query, message_history=self.history.messages
            )

            if isinstance(result, AgentRunResult):
                return str(result.output)
            return str(result)

        except Exception:
            logger.exception("An error occurred during specialist execution:")
            return "Sorry, I encountered an error while processing your request."

    def process_query(self, query: str) -> str:
        """Processes a single user query and triggers the background RAG pipeline."""
        self.history.add("user", query)

        try:
            route = self._get_routing_decision(query)
            response = self._execute_specialist_task(route)
        except Exception:
            logger.exception("An unexpected error occurred in process_query:")
            response = (
                "I'm sorry, I ran into a problem and couldn't complete your request."
            )

        self.history.add("assistant", response)
        # self.rag_pipeline.run_in_background(self.history)

        return response

    def start_cli(self):
        """Starts the command-line interface for interacting with the assistant."""
        console.print("\n🗣️ You can now chat with Val. Type 'exit' to quit.")
        while True:
            try:
                user_query = input("You: ")
                if user_query.lower() in ["exit", "quit"]:
                    break

                console.print("\nVal: ", end="")
                response = self.process_query(user_query)
                console.print(f"{response}\n")

            except (KeyboardInterrupt, EOFError):
                break

        console.print("👋 Goodbye!")
        sys.exit(0)


def start_assistant():
    """Initializes and runs the ValAI assistant CLI."""
    ass = Assistant()
    ass.start_cli()


if __name__ == "__main__":
    start_assistant()
