import asyncio
import os
from logging import exception

from dotenv import load_dotenv

from llm_module.llm_instance import get_client
from llm_module.system_prompts import personality_system_prompt
from utility_scripts.system_logging import setup_logger
from llm_module.llm_create import LLM_CONFIG

from ollama import Client, chat


# configure logging
logger = setup_logger(__name__)

# --- Environment ---
load_dotenv()
os.environ["OLLAMA_API_KEY"] = os.getenv("OLLAMA_API")

# get LLM CONFIG
CONFIG = LLM_CONFIG.ISABEL


async def llm_internet_search(bot, message) -> list:
    client = get_client()

    # Map tool names to actual functions
    TOOLS = {
        "web_search": client.web_search,
        "web_fetch": client.web_fetch
    }

    system_prompt = {
        "role": "system", "content":
            personality_system_prompt
    }

    user_prompt = {"role": "user", "content": message.content}

    messages = [
        system_prompt,
        user_prompt
    ]

    response = await asyncio.to_thread(
        chat,
        model=CONFIG.TOOL_MODEL,
        messages=messages,
        options={
            "num_ctx": CONFIG.DEFAULT_CONTEXT,
            "temperature": CONFIG.DEFAULT_TEMPERATURE,
            "think": True
        },
        tools=list(TOOLS.values()),
        stream=False
    )

    # todo -- add these and the token info to the logs
    # print response info
    if response.message.thinking:
        # print('Thinking: ', response.message.thinking)
        pass
    if response.message.content:
        # print('Content: ', response.message.content)
        pass

    # manage tools
    tool_calls = []

    if response.message.tool_calls:
        logger.debug(f'Tool calls: {response.message.tool_calls}')
        # get tool from called tools
        for tool_call in response.message.tool_calls:

            header = f'```--- {tool_call.function.name} Result ---\n'
            footer = '\n```'

            function_to_call = TOOLS.get(tool_call.function.name)
            if function_to_call:
                # execute tool function and append results in a message
                args = tool_call.function.arguments
                result = function_to_call(**args)

                # get first result
                first_result = result.results[0]  # get the first WebSearchResult
                first_content = first_result.content  # get the content
                logger.debug(first_content[:200])

                result_string = header + first_content + footer

                tool_calls.append(result_string)

            else:
                raise InvalidToolError(tool_call.function, tool_call.function.name)

    return tool_calls


class InvalidToolError(Exception):
    """Exception raised for invalid age values in a specific application."""
    def __init__(self, tool, message="Tool Not Found"):
        self.tool = tool
        super().__init__(f'Tool: {message} Not found or Invalid')