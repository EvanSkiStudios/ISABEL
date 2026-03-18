import asyncio
import os

import discord
import time
from discord.ext import commands, voice_recv


class VoiceListener(voice_recv.VoiceRecvClient):
    def __init__(self, client, channel, sink):
        # pass both required arguments to the parent
        super().__init__(client, channel)
        self.sink = sink

    def on_speaking_start(self, user):
        print(f"{user} started speaking")

        self.sink.recording_users.add(user)
        self.sink.audio_data[user] = bytearray()

    def on_speaking_stop(self, user):
        print(f"{user} stopped speaking")

        self.sink.recording_users.discard(user)

        pcm_data = self.sink.audio_data.pop(user, None)

        if pcm_data:
            filename = f"{user.id}_{int(time.time())}.mp3"


class MySink(voice_recv.AudioSink):
    def __init__(self):
        super().__init__()
        self.audio_data = {}        # user → bytearray()
        self.last_audio_time = {}   # user → last packet timestamp

    def wants_opus(self) -> bool:
        return True  # capture raw Opus, no PCM decoding

    def write(self, user, data):
        if user not in self.audio_data:
            print(f"{user} started speaking (Opus fallback)")
            self.audio_data[user] = bytearray()

        self.audio_data[user] += data.opus  # save raw Opus
        self.last_audio_time[user] = time.time()

    def cleanup(self):
        self.audio_data.clear()
        self.last_audio_time.clear()


async def monitor_silence(sink, min_silence=1.0):
    os.makedirs("recordings", exist_ok=True)
    while True:
        await asyncio.sleep(0.5)
        now = time.time()
        for user in list(sink.audio_data.keys()):
            if now - sink.last_audio_time[user] > min_silence:
                print(f"{user} stopped speaking, saving Opus")
                opus_data = sink.audio_data.pop(user)
                sink.last_audio_time.pop(user, None)
                if opus_data:
                    filename = f"recordings/{user.id}_{int(now)}.opus"
                    with open(filename, "wb") as f:
                        f.write(opus_data)
