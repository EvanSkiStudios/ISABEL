import asyncio
import os
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands

from discord_module.utilities.message_delete_later import delete_later
from utility_scripts.namespace_utility import namespace
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

# Load Env
load_dotenv()


config_dict = {
    "MASTER_USER_ID": os.getenv("MASTER_USER_ID"),
}
CONFIG = namespace(config_dict)


class Censor(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="censor", description="puts messages in spoilers")
    async def Censor(self, interaction, message_ids: str):
        logger.debug(f'Command issued: censor by {interaction.user}')

        await interaction.response.defer(ephemeral=True)

        if interaction.user.id != int(CONFIG.MASTER_USER_ID):
            bot_msg = await interaction.followup.send(
                "This is an Admin only command.",
                ephemeral=True
            )
            return

        split_message_ids = [m.strip() for m in message_ids.split(',')]

        censored = []
        failed = []

        for msg_id in split_message_ids:
            try:
                msg_id = int(msg_id)
                msg = await interaction.channel.fetch_message(msg_id)
                if msg.author == self.client.user:

                    if not msg.content.startswith("||"):
                        await msg.edit(content=f"||{msg.content}||")
                    censored.append(msg_id)

                else:
                    failed.append((msg_id, "Not sent by bot"))
            except discord.NotFound:
                failed.append((msg_id, "Message not found"))
            except discord.Forbidden:
                failed.append((msg_id, "Missing permissions"))
            except discord.HTTPException as e:
                failed.append((msg_id, f"HTTP error: {e}"))

        report = []
        if censored:
            report.append(f"✅ Censored: {', '.join(map(str, censored))}")
        if failed:
            report.append("❌ Failed:\n" + "\n".join(f"{i}: {reason}" for i, reason in failed))

        logger.debug("\n".join(report))
        bot_msg = await interaction.followup.send(
            f"Censored: ({len(censored)}) Messages",
            ephemeral=True
        )
        asyncio.create_task(delete_later(bot_msg, 6))


async def setup(bot: commands.Bot):
    await bot.add_cog(Censor(bot))
