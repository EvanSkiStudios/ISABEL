import wave
import struct
from discord.ext.voice_recv import AudioSink, VoiceRecvClient

from ctypes.util import find_library
import os
from pathlib import Path

# Path to the current script
base_dir = Path(__file__).parent
# Directory next to the script
target_dir = base_dir / "opus_lib"

# Load the DLL manually
os.environ["PATH"] += fr";{target_dir}"
lib_location = find_library("opus")

import opuslib


class OpusSink(AudioSink):
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self._buffer = bytearray()
        # 48kHz, 2 channels stereo
        self.decoder = opuslib.Decoder(48000, 1)

    def wants_opus(self) -> bool:
        return True

    def write(self, user, data):
        if data.opus:
            try:
                # 960 samples per channel → 20ms frame at 48kHz
                pcm = self.decoder.decode(data.opus, 960)
                self._buffer.extend(pcm)
            except opuslib.OpusError:
                pass  # skip corrupted frames

    def cleanup(self):
        # Save decoded PCM properly as WAV
        with wave.open(self.file_path, "wb") as wf:
            wf.setnchannels(1)       # stereo
            wf.setsampwidth(2)       # 16-bit PCM
            wf.setframerate(48000)   # 48kHz
            wf.writeframes(self._buffer)
