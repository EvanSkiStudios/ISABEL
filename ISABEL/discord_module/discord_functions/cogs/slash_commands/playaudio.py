from pathlib import Path
import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)


class PlayAudio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Compute the path to the MP3 relative to this file
        self.audio_file = (
                Path(__file__)
                .parent.parent.parent.parent.parent / "discord_voice_module" / "assets" / "test" / "nekomonogatari.mp3"
        )

    @app_commands.command(name="play", description="Play an mp3 file in your voice channel")
    async def play(self, interaction):
        logger.debug(f'Command issued: play by {interaction.user}')
        await interaction.response.defer(ephemeral=True)

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("You need to be in a voice channel to play audio!", ephemeral=True)
            return

        channel = interaction.user.voice.channel

        # Connect to voice channel (reuse if already connected)
        voice_client = interaction.guild.voice_client or await channel.connect()

        # Play MP3
        audio_source = discord.FFmpegPCMAudio(str(self.audio_file))

        if not voice_client.is_playing():
            voice_client.play(audio_source, after=lambda e: logger.debug(f"Playback finished: {e}"))
            await interaction.followup.send("Playing audio now!", ephemeral=True)
        else:
            await interaction.followup.send("Already playing audio!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(PlayAudio(bot))

