import glob
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import yaml
from loguru import logger
from pydantic import BaseModel
from pydantic_ai import Agent

from valai.config import get_settings
from valai.core.llm_factory import get_llm_client
from valai.core.route import create_dynamic_route_model
from valai.core.tool_registry import TOOL_REGISTRY


@lru_cache
def get_enabled_agents() -> List[str]:
    """Reads agent toggles from settings and returns a list of properly formatted,
    human-readable agent names (e.g., "Code Agent").
    """
    settings = get_settings()
    toggler = settings.agent_toggler.model_dump()
    enabled_agents = []
    for toggle_name, is_enabled in toggler.items():
        if is_enabled:
            processed_name = toggle_name.replace("use_", "")
            parts = processed_name.split("_")
            capitalized_parts = [part.capitalize() for part in parts]
            final_name = " ".join(capitalized_parts)
            enabled_agents.append(final_name)

    logger.info(f"Enabled agents: {enabled_agents}")
    return enabled_agents


# Dynamically create the Route class based on enabled agents.
Route: BaseModel = create_dynamic_route_model(get_enabled_agents())  # type: ignore


@lru_cache
def load_agents() -> Dict[str, Agent]:
    """Discovers and loads configurations for all enabled agents. It selectively
    injects a timestamp into the Search Agent's prompt for better context.
    """
    agents = {}
    enabled_agent_names = get_enabled_agents()

    agent_configs = {}
    for config_path in glob.glob("config/agents/*.yaml"):
        stem = Path(config_path).stem
        parts = stem.split("_")
        capitalized_parts = [part.capitalize() for part in parts]
        formatted_name = " ".join(capitalized_parts)
        agent_configs[formatted_name] = config_path

    for agent_name in enabled_agent_names:
        config_path = agent_configs.get(agent_name)
        if not config_path:
            logger.warning(
                f"Config file for enabled agent '{agent_name}' not found. Skipping."
            )
            continue

        logger.debug(f"Loading enabled agent: {agent_name} from {config_path}")
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        agent_tools = [
            TOOL_REGISTRY[tool_name]
            for tool_name in config.get("tools", [])
            if tool_name in TOOL_REGISTRY
        ]

        prompt = config["system_prompt"]
        if agent_name == "Search Agent":
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prompt = (
                f"The current date and time is: {timestamp}. Use this information to "
                f"better understand user queries about recent events. {config['system_prompt']}"
            )
            logger.info(f"Prompt: {prompt}")
            logger.info(f"Injecting timestamp into '{agent_name}' prompt.")

        agents[agent_name] = Agent(
            model=get_llm_client(),
            system_prompt=prompt,
            tools=agent_tools,
            retries=3,
        )

    return agents


@lru_cache
def load_router() -> Agent:
    """Loads the main router agent with a system prompt that is dynamically generated
    to include only the currently enabled, properly formatted agent names.
    """
    with open("config/router.yaml", "r") as f:
        config = yaml.safe_load(f)
        base_prompt = config["system_prompt"]

    enabled_agents = get_enabled_agents()
    available_specialists = "\n".join([f"- {name}" for name in enabled_agents])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    full_prompt = (
        f"{base_prompt}\n\n"
        f"The current date and time is: {timestamp}.\n"
        f"Here are the ONLY available specialists you can route to:\n{available_specialists}"
    )

    logger.info("Router prompt configured with dynamic specialist list and timestamp.")
    return Agent(model=get_llm_client(), system_prompt=full_prompt, tools=[], retries=3)
