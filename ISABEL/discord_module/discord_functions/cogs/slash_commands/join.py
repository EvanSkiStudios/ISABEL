import asyncio
import os

from discord import app_commands
from discord.ext import commands, voice_recv

from discord_module.utilities.message_delete_later import delete_later
from discord_voice_module.custom_audio_sink import OpusSink
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
            voice_client = interaction.guild.voice_client

            # join or move to the voice channel
            if voice_client:
                # if voice_client.channel != channel:
                # await voice_client.move_to(channel)
                await voice_client.disconnect()
                voice_client = await channel.connect(cls=voice_recv.VoiceRecvClient)
                msg = await interaction.followup.send(f"I have Moved to the voice channel: {channel.name}")
            else:
                voice_client = await channel.connect(cls=voice_recv.VoiceRecvClient)
                msg = await interaction.followup.send(f"I have joined the voice channel: {channel.name}")

            # create a folder for recordings if it doesn't exist
            os.makedirs("recordings", exist_ok=True)

            # Start recording with WaveSink
            sink = OpusSink("recordings/output.wav")

            logger.info("Listening")
            voice_client.listen(sink)

            await asyncio.sleep(5)  # duration

            voice_client.stop_listening()
            logger.info("Done listening")

            sink.cleanup()

        else:
            msg = await interaction.followup.send("You are not in a voice channel!")

        asyncio.create_task(delete_later(msg, 6))


async def setup(bot: commands.Bot):
    await bot.add_cog(Join(bot))
