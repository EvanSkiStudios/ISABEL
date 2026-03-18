import asyncio
from discord import app_commands
from discord.ext import commands, voice_recv
from discord_voice_module.voice_listener import MySink, VoiceListener, monitor_silence
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
            sink = MySink()

            # handle existing connection
            vc = interaction.guild.voice_client
            if vc:
                if vc.channel != channel:
                    await vc.move_to(channel)
                await interaction.followup.send(f"Moved to: {channel.name}")
            else:
                # connect first without passing the sink
                vc: voice_recv.VoiceRecvClient = await channel.connect(
                    cls=voice_recv.VoiceRecvClient,
                    self_deaf=False
                )

                # attach the sink after connection
                vc.listen(sink)

                await interaction.followup.send(f"Joined: {channel.name}")

                # start monitoring silence
                asyncio.create_task(monitor_silence(sink))
        else:
            await interaction.followup.send("You are not in a voice channel!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Join(bot))
