import warnings
import whisper

# Suppress FP16 CPU warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")


async def whisper_transcribe(file_path):
    # turbo, base, medium
    model = whisper.load_model("base")
    result = model.transcribe(str(file_path))
    return result["text"]
