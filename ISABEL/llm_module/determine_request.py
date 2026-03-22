from discord_module.utilities.attachments.discord_attachments_manager import get_message_attachments
from llm_module.tools.web_search.search_determinator.internet_search_determinator import is_search_request


def classify_request(message, text: str) -> tuple:
    message_attachments = get_message_attachments(message)

    if message_attachments:
        return "attachment", message_attachments

    if is_search_request(text):
        return ("search",)

    # if is_weather_request(text):
    #    return ("weather_search",)

    # if none then just normal conversation
    return ("conversation",)
