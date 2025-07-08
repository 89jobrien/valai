from typing import List, Literal, Type

from pydantic import BaseModel, Field, create_model


def create_dynamic_route_model(enabled_agents: List[str]) -> Type[BaseModel]:
    """Dynamically creates a Pydantic model for routing decisions based on a list of enabled agents.
    This ensures the router's output is validated against only the agents that are currently active.

    Args:
        enabled_agents: A list of names of the agents that are enabled.

    Returns:
        A dynamically created Pydantic BaseModel class for the route.

    """
    if not enabled_agents:
        # If for some reason no agents are enabled, create a model that can't be satisfied.
        enabled_agents = ["NoAgentsEnabled"]

    # The first argument to Literal must be a literal value, not a variable.
    # We use create_model to dynamically construct the field with the correct Literal type.
    DynamicRoute = create_model(  # noqa
        "Route",
        specialist_name=(
            Literal[tuple(enabled_agents)],  # type: ignore
            Field(
                ...,
                description="The name of the specialist agent to route the query to.",
            ),
        ),
        query_for_specialist=(
            str,
            Field(
                ...,
                description=(
                    "The query to be sent to the specialist. This might be the "
                    "original user query or a rephrased version for clarity."
                ),
            ),
        ),
        __doc__="The routing decision made by the Router agent.",
    )
    return DynamicRoute


# from typing import List, Type

# from pydantic import BaseModel, Field, create_model

# # TODO: add in Route class


# def create_dynamic_route_model(enabled_agents: List[str]) -> Type[BaseModel]:
#     """Dynamically creates a Pydantic model for routing decisions based on a list of enabled agents.
#     This ensures the router's output is validated against only the agents that are currently active.

#     Args:
#         enabled_agents: A list of names of the agents that are enabled.

#     Returns:
#         A dynamically created Pydantic BaseModel class for the route.

#     """
#     if not enabled_agents:
#         enabled_agents = ["NoAgentsEnabled"]

#     DynamicRoute = create_model(  # noqa
#         "Route",
#         specialist_name=(
#             [tuple(enabled_agents)],
#             Field(
#                 ...,
#                 description="The name of the specialist agent to route the query to.",
#             ),
#         ),
#         query_for_specialist=(
#             str,
#             Field(
#                 ...,
#                 description=(
#                     "The query to be sent to the specialist. This might be the "
#                     "original user query or a rephrased version for clarity."
#                 ),
#             ),
#         ),
#         __doc__="The routing decision made by the Router agent.",
#     )
#     return DynamicRoute


# class Route(BaseModel):
#     """The routing decision made by the Router agent."""

#     specialist_name: str = Field(
#         ...,
#         description="The name of the specialist agent to route the query to.",
#     )
#     query_for_specialist: str = Field(
#         ...,
#         description=(
#             "The query to be sent to the specialist. This might be the "
#             "original user query or a rephrased version for clarity."
#         ),
#     )
