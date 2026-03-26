import copy

from llm_module.system_prompts import personality_system_prompt
from memory_module.process_message import process_message


async def build_web_system_prompt(bot, message, prompt_data):
    message_cache = prompt_data["message_cache"]
    file_data = prompt_data["attachment_data"]

    if file_data is None:
        file_data = {"text": None, "audio": None}

    system_prompt = {"role": "system", "content": personality_system_prompt}

    user_content = await process_message(bot, message)

    user_prompt = copy.deepcopy(user_content)
    cached_user_message = copy.deepcopy(user_content)

    # File data
    text_data = file_data["text"]
    if text_data:
        user_prompt["content"] += text_data
        cached_user_message["content"] += text_data

    full_prompt = [
        system_prompt,
        user_prompt
    ]

    return {
        "full_prompt": full_prompt,
        "system_prompt": system_prompt,
        "message_cache": [],
        "cached_user_message": cached_user_message
    }