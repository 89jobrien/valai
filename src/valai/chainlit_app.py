import chainlit as cl

from valai.agents.base import get_enabled_agents

# from mcp import ClientSession
from valai.core.assistant import Assistant

# TODO: To get a sidebar with chat history, auth and a database need to be implemented
# @cl.password_auth_callback
# async def auth_callback(username: str, password: str):
#     # Fetch the user matching username from your database
#     # and compare the hashed password with the value stored in the database
#     if (username, password) == ("admin", "admin"):
#         return cl.User(
#             identifier="admin", metadata={"role": "admin", "provider": "credentials"}
#         )
#     else:
#         return None

enabled_agents = get_enabled_agents()


@cl.on_chat_start
async def start_chat():
    cl.user_session.set("assistant", Assistant())
    await cl.Message(
        content="""Hello! I am ValAI, your AI assistant.

I can help with a variety of tasks by routing your requests to specialized agents. How can I assist you today?

Available agents: """
        + ", ".join(enabled_agents),
        author="ValAI",
    ).send()


# @cl.on_mcp_connect
# async def on_mcp(connection, session: ClientSession):
#     # List available tools
#     result = await session.list_tools()

#     # Process tool metadata
#     tools = [
#         {
#             "name": t.name,
#             "description": t.description,
#             "input_schema": t.inputSchema,
#         }
#         for t in result.tools
#     ]

#     # Store tools for later use
#     mcp_tools = cl.user_session.get("mcp_tools", {})
#     mcp_tools[connection.name] = tools
#     cl.user_session.set("mcp_tools", mcp_tools)

#     # # Send tools to the user
#     # await cl.Message(
#     #     content=f"Available tools: {', '.join([t['name'] for t in tools])}",
#     #     author="ValAI",
#     # ).send()


# @cl.step(type="tool")
# async def call_tool(tool_use):
#     tool_name = tool_use.name
#     tool_input = tool_use.input

#     # Find appropriate MCP connection for this tool
#     mcp_name = find_mcp_for_tool(tool_name)

#     # Get the MCP session
#     mcp_session, _ = cl.context.session.mcp_sessions.get(mcp_name)

#     # Call the tool
#     result = await mcp_session.call_tool(tool_name, tool_input)

#     return result


@cl.on_message
async def main(message: cl.Message):
    assistant = cl.user_session.get("assistant")
    if assistant is None:
        await cl.Message(
            content="Error: Assistant not initialized.", author="System"
        ).send()
        return

    final_response = ""
    async for chunk in assistant.process_query(message.content):
        if "final_answer" in chunk:
            final_response = chunk["final_answer"]
        elif "status" in chunk:
            await cl.Message(content=chunk["status"], author="System").send()
    await cl.Message(content=final_response, author="ValAI").send()
