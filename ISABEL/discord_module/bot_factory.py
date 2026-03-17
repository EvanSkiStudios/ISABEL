import discord
from discord.ext import commands
from discord_module.config import get_config
from discord_module.events import register_events


# set discord_functions intents
intents = discord.Intents.default()
intents.message_content = True
intents.emojis_and_stickers = True

# gather namespace config
CONFIG = get_config()


class MyBot(commands.Bot):
    async def setup_hook(self):
        # Load cogs here
        cogs = [
            "discord_module.discord_functions.cogs.bot_commands",
            "discord_module.discord_functions.cogs.slash_commands.parrot",
            # "discord_module.discord_functions.cogs.slash_commands.tts",
        ]
        for cog in cogs:
            await self.load_extension(cog)

        # Global (takes time to propagate)
        await self.tree.sync()


def create_bot():
    bot = MyBot(
        command_prefix=["$s "],
        intents=intents,
        status=discord.Status.online
    )

    register_events(bot)
    return bot

