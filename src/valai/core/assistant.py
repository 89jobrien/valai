import re
from datetime import datetime
from typing import AsyncGenerator, Dict

from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult

from valai.agents.base import Route, load_agents, load_router
from valai.core.console import console
from valai.core.history import ConversationHistory

# from valai.core.rag_pipeline import BackgroundRAG


class Assistant:
    """Orchestrates the agent routing and execution logic asynchronously."""

    def __init__(self):
        """Initializes the assistant and all its components."""
        logger.add(
            "logs/valai_assistant.log",
            rotation="10 MB",
            level="INFO",
            backtrace=True,
            diagnose=True,
        )
        console.log("🚀 Initializing ValAI Assistant...")
        self.router: Agent = load_router()
        self.specialists: Dict[str, Agent] = load_agents()
        self.history = ConversationHistory()
        # self.rag_pipeline = BackgroundRAG()
        console.log("✅ Assistant is ready.")

    async def _get_routing_decision(self, query: str) -> Route:  # type: ignore
        """Asynchronously routes the user's query to a specialist."""
        raw_result = await self.router.run(
            user_prompt=query,
            message_history=self.history.messages,
            output_type=Route,  # type: ignore
        )  # type: ignore

        if isinstance(raw_result, AgentRunResult):
            route = raw_result.output
        else:
            route = Route.model_validate(raw_result)

        if not isinstance(route, Route):  # type: ignore
            raise TypeError(
                f"Extracted output is not a valid Route object: {type(route)}"
            )

        return route

    async def _execute_specialist_task(self, route: Route) -> str:  # type: ignore
        """Asynchronously executes the task using the chosen specialist.
        This method is now clean, with the guardrail logic moved up.
        """
        specialist_name = route.specialist_name
        specialist_query = route.query_for_specialist

        if specialist_name not in self.specialists:
            return f"Error: Could not find specialist '{specialist_name}'."

        specialist = self.specialists[specialist_name]
        result = await specialist.run(
            user_prompt=specialist_query, message_history=self.history.messages
        )

        if isinstance(result, AgentRunResult):
            return str(result.output)
        return str(result)

    async def process_query(self, query: str) -> AsyncGenerator[Dict[str, str], None]:
        """Processes a query, applying a smart guardrail for the Search Agent
        before yielding status updates and the final answer.
        """
        self.history.add("user", query)

        try:
            yield {"status": "🧠 Thinking... (Routing query)"}
            route = await self._get_routing_decision(query)

            if route.specialist_name == "Search Agent":
                # Check if the user's query already contains a 4-digit year.
                user_query_has_year = re.search(r"\b(19|20)\d{2}\b", query)

                # Only modify the query if the user did NOT specify a year.
                if not user_query_has_year:
                    current_year_str = str(datetime.now().year)
                    # To be safe, we remove any incorrect year the router might have added
                    # and append the correct current year.
                    query_for_specialist = re.sub(
                        r"\s*\b(19|20)\d{2}\b\s*", " ", route.query_for_specialist
                    ).strip()
                    modified_query = f"{query_for_specialist} {current_year_str}"

                    console.log(
                        f"[bold yellow]Query modified for Search Agent: '{route.query_for_specialist}' -> '{modified_query}'[/bold yellow]"
                    )
                    # Update the route object before it's passed to the specialist.
                    route.query_for_specialist = modified_query

            yield {"status": f"🚦 Routing to: {route.specialist_name}"}
            yield {"status": f"🛠️ Specialist '{route.specialist_name}' is working..."}
            response = await self._execute_specialist_task(route)

        except Exception as e:
            logger.exception(f"An unexpected error occurred in process_query: {e}")
            response = (
                "I'm sorry, I ran into a problem and couldn't complete your request."
            )

        self.history.add("assistant", response)
        # self.rag_pipeline.run_in_background(self.history)

        yield {"final_answer": response}
