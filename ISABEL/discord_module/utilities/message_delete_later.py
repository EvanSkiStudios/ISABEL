import asyncio
import discord


async def delete_later(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except (discord.NotFound, discord.Forbidden):
        pass  # expected errors

    pass  # ignore if already deleted or fails
