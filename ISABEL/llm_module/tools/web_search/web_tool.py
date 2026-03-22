import asyncio
import os
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


async def llm_internet_search(bot, message):
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

    # print response info
    if response.message.thinking:
        print('Thinking: ', response.message.thinking)
    if response.message.content:
        print('Content: ', response.message.content)

    # manage tools
    if response.message.tool_calls:
        print('Tool calls: ', response.message.tool_calls)
        # get tool from called tools
        for tool_call in response.message.tool_calls:

            function_to_call = TOOLS.get(tool_call.function.name)
            if function_to_call:
                # execute tool function and append results in a message
                args = tool_call.function.arguments
                result = function_to_call(**args)

                # get first result
                first_result = result.results[0]  # get the first WebSearchResult
                first_content = first_result.content  # get the content
                print(first_content)

                # todo -- Chat Model is not using the results of the tool call
                # will have to pass it in a system prompt probably

                return {'role': 'tool', 'content': first_content, 'tool_name': tool_call.function.name}

            else:
                return {'role': 'tool', 'content': f'Tool {tool_call.function.name} not found', 'tool_name': tool_call.function.name}


if __name__ == "__main__":

    class FakeMessage:
        def __init__(self, content):
            self.content = content

    # Create a client with your API key
    client = Client(
        host="https://ollama.com",  # required for cloud API
        headers={"Authorization": f"Bearer {os.getenv('OLLAMA_API')}"}
    )

    msg = FakeMessage("search the internet for the current stock price of nvidia")

    response = asyncio.run(llm_internet_search(None, msg))
    logger.info(response)
