from discord import app_commands
from discord.ext import commands

from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)


# pip install -U "discord.py[voice]"

class Join(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="join", description="Have Isabel join your voice channel")
    async def Join(self, interaction):
        logger.debug(f'Command issued: join by {interaction.user}')
        await interaction.response.defer()

        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()
            await interaction.followup.send(f"I have joined the voice channel: {channel.name}")
        else:
            await interaction.followup.send("You are not in a voice channel!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Join(bot))
