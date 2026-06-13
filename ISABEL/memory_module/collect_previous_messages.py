import discord

from discord_module.message_filters import bots_blacklist, message_is_slash_reply
from memory_module.process_message import process_message


# todo -- Conversation history is really effecting prompt generation and the time it takes to process things
# todo -- Need better way to handle chats from multiple users

async def get_message_replied_to_author(message):
    # if we get None, skip the message, else we get an id, and then we check if we should skip

    if message.reference is None:
        # if we cant find the reply to message then just skip this message
        return None

    referenced = message.reference.resolved

    if referenced is None:
        try:
            referenced = await message.channel.fetch_message(message.reference.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            # if we get an error best to just skip this message then
            return None

    return referenced.author.id


# filters message based on rules
async def skip_message(message):
    if message.author.id in bots_blacklist:
        return True

    # ignore embeds and empty messages
    if message.content == "" and len(message.embeds) == 0:
        return True

    if await message_is_slash_reply(message):
        return True

    if message.type in {discord.MessageType.chat_input_command, discord.MessageType.thread_created}:
        return True

    # todo -- remove messages from users that mention, banned bots
    if message.type == discord.MessageType.reply:

        # get if reply is to a banned bot
        replied_to_user_id = await get_message_replied_to_author(message)
        if replied_to_user_id is None:
            return True

        if replied_to_user_id in bots_blacklist:
            # current message is a reply to a banned bot, ignore this message
            return True

    # all checks passed message is fine
    return False


# MAIN INPUT FUNCTION
async def gather_past_messages(bot, message, amount=20):
    channel = message.channel

    messages = []
    async for past_message in channel.history(limit=amount, before=message):

        # filter past messages
        if await skip_message(past_message):
            continue

        messages.append(await process_message(bot, past_message))

    messages.reverse()

    return messages
