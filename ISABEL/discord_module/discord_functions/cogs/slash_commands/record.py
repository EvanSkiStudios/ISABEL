from discord import app_commands
from discord.ext import commands, voice_recv

from utility_scripts.system_logging import setup_logger
import time

# configure logging
logger = setup_logger(__name__)


class Record(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.voice_client = None
        self.sink = None
        self.file = None
        self.recording = False
        self.warmup_complete = False

    class WarmupSink(voice_recv.AudioSink):
        def __init__(self, wrapped_sink, parent_cog):
            super().__init__()
            self.wrapped_sink = wrapped_sink
            self.parent_cog = parent_cog
            self.packet_count = 0

        def wants_opus(self) -> bool:
            return False  # We want PCM data

        def write(self, user, data):
            self.packet_count += 1
            # Wait for 50 packets before writing (warmup period)
            if self.packet_count > 50:
                if not self.parent.warmup_complete:
                    self.parent.warmup_complete = True
                    logger.info("Warmup complete, starting recording")
                self.wrapped_sink.write(user, data)

        def cleanup(self):
            self.wrapped_sink.cleanup()

    @app_commands.command(name="record", description="Have Isabel record")
    async def Record(self, interaction):
        logger.debug(f'Command issued: record by {interaction.user}')
        await interaction.response.defer()

        if not interaction.user.voice:
            await interaction.followup.send("You are not in a voice channel!")
            return

        channel = interaction.user.voice.channel
        voice_channel = interaction.guild.voice_client

        if voice_channel and voice_channel.is_connected():
            await voice_channel.disconnect()

        try:
            self.voice_client = await channel.connect(cls=voice_recv.VoiceRecvClient)
            self.file = open('recording.wav', 'wb')
            wave_sink = voice_recv.WaveSink(self.file)
            self.sink = self.WarmupSink(wave_sink, self)
            self.warmup_complete = False

            def after_callback(error):
                if error:
                    logger.error(f"Recording error: {error}")
                self.recording = False

            self.voice_client.listen(self.sink, after=after_callback)
            self.recording = True
            await interaction.followup.send("Recording started (warming up...)")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            await interaction.followup.send(f"Failed to start recording: {e}")

    @app_commands.command(name="stop", description="Stop recording")
    async def stop(self, interaction):
        if not self.recording:
            await interaction.response.send_message("Not currently recording!")
            return

        try:
            if self.voice_client and self.voice_client.is_listening():
                self.voice_client.stop_listening()
                await self.voice_client.disconnect()

            if self.sink:
                self.sink.cleanup()
            if self.file:
                self.file.close()

            self.recording = False
            await interaction.response.send_message("Recording stopped and saved!")
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            await interaction.response.send_message(f"Error stopping recording: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Record(bot))
