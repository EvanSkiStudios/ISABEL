from discord_module.utilities.attachments.discord_attachments_manager import get_message_attachments


def classify_request(message, text: str) -> tuple:
    message_attachments = get_message_attachments(message)

    if message_attachments:
        return "attachment", message_attachments

    # if none then just normal conversation
    return ("conversation",)
