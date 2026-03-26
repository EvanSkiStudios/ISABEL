import asyncio

from ollama import chat

from llm_module.generators.web_search.web_system_prompt import build_web_system_prompt
from llm_module.llm_create import LLM_CONFIG
from llm_module.llm_instance import get_client

from llm_module.process_response import process_response
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

CONFIG = LLM_CONFIG.ISABEL


class InvalidToolError(Exception):
    """Exception raised for invalid age values in a specific application."""
    def __init__(self, tool, message="Tool Not Found"):
        self.tool = tool
        super().__init__(f'Tool: {message} Not found or Invalid')


async def llm_generate_web_response(bot, message, attachments=None):
    client = get_client()

    # Map tool names to actual functions
    TOOLS = {
        "web_search": client.web_search,
        "web_fetch": client.web_fetch
    }

    prompt_info = {
        "message_cache": [],
        "attachment_data": attachments,
    }

    prompt_data = await build_web_system_prompt(bot, message, prompt_info)

    full_prompt = prompt_data["full_prompt"]
    system_prompt = prompt_data["system_prompt"]
    message_cache = prompt_data["message_cache"]
    cached_user_message = prompt_data["cached_user_message"]

    response = await llm_web_response(TOOLS, full_prompt)
    response_data = process_response(response, system_prompt, message_cache)

    full_prompt = process_tool_calls(TOOLS, response, full_prompt, message_cache)
    final_response = await llm_web_response(TOOLS, full_prompt)

    final_response_data = process_response(final_response, system_prompt, message_cache)

    final_response_data["user"] = cached_user_message

    if attachments:
        response_data["file_txt"] = attachments["text"]

    return final_response_data


def process_tool_calls(tools, response, full_prompt, message_cache):
    if response.message.tool_calls:
        logger.debug(f'Tool calls: {response.message.tool_calls}')
        # get tool from called tools
        for tool_call in response.message.tool_calls:
            function_to_call = tools.get(tool_call.function.name)
            if function_to_call:
                # execute tool function and append results in a message
                args = tool_call.function.arguments
                result = function_to_call(**args)

                # todo -- Debug
                print('Result: ', str(result)[:200] + '...')

                tool_message = {
                    'role': 'tool',
                    'content': str(result)[:2000 * 4],
                    'tool_name': tool_call.function.name
                }

                full_prompt.append(tool_message)
                message_cache.append(tool_message)
            else:
                raise InvalidToolError(tool_call.function, tool_call.function.name)

    return full_prompt


async def llm_web_response(tools, full_prompt):

    response = await asyncio.to_thread(
        chat,
        model=CONFIG.TOOL_MODEL,
        messages=full_prompt,
        options={
            "num_ctx": CONFIG.DEFAULT_CONTEXT,
            "temperature": CONFIG.DEFAULT_TEMPERATURE,
            "think": True
        },
        tools=list(tools.values()),
        stream=False
    )

    full_prompt.append(response.message)

    return response

