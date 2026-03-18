import asyncio
from ollama import chat

from llm_module.llm_create import LLM_CONFIG, llm_create
from llm_module.system_prompts import personality_system_prompt
from tts_module.elevenlabs_voice import text_to_speech
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

CONFIG = LLM_CONFIG.ISABEL

message_cache = []


async def llm_test_generate(user_input):
    global message_cache
    llm_model = CONFIG.MODEL_NAME

    system_prompt = {"role": "system", "content": personality_system_prompt}

    full_prompt = [
        system_prompt,
        *message_cache,
        {'role': 'user', 'content': user_input}
    ]

    response = await asyncio.to_thread(
        chat,
        model=llm_model,
        messages=full_prompt,
        options={
            "num_ctx": CONFIG.DEFAULT_CONTEXT,
            "temperature": CONFIG.DEFAULT_TEMPERATURE,
            "think": False
        },
        stream=False
    )

    message_cache += [
        {'role': 'user', 'content': user_input},
        {'role': 'assistant', 'content': response.message.content},
    ]
    return response.message.content


async def input_loop():
    while True:
        user_input = input("> ").lower()
        if user_input == "/exit":
            break

        response = await llm_test_generate(user_input)
        logger.info(response)
        # await text_to_speech(response)


if __name__ == "__main__":
    llm_create()
    asyncio.run(input_loop())
