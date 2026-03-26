import asyncio

from discord import app_commands
from discord.ext import commands

from discord_module.utilities.message_delete_later import delete_later
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)


class Leave(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="leave", description="Have Isabel leave the voice channel")
    async def Leave(self, interaction):
        logger.debug(f'Command issued: leave by {interaction.user}')
        await interaction.response.defer(ephemeral=True)

        voice_client = interaction.guild.voice_client  # get the voice client for this guild
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            msg = await interaction.followup.send("I have left the voice channel.", ephemeral=True)
        else:
            msg = await interaction.followup.send("I am not in a voice channel to leave.", ephemeral=True)

        asyncio.create_task(delete_later(msg, 6))


async def setup(bot: commands.Bot):
    await bot.add_cog(Leave(bot))
