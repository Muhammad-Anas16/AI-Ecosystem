import io
import wave
from pathlib import Path

from piper import PiperVoice
from piper.download_voices import download_voice

VOICE_NAME = "en_US-lessac-medium"
VOICES_DIR = Path(__file__).parent / "voices"
VOICE_PATH = VOICES_DIR / f"{VOICE_NAME}.onnx"

_voice = None


def ensure_downloaded():
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    if not VOICE_PATH.exists():
        print(f"[TTS-Piper] '{VOICE_NAME}' voice pehli baar download ho rahi hai...")
        download_voice(VOICE_NAME, VOICES_DIR)
        print("[TTS-Piper] Voice ready.")


def get_voice():
    global _voice
    if _voice is None:
        ensure_downloaded()
        _voice = PiperVoice.load(str(VOICE_PATH))
    return _voice


def synthesize_to_wav_bytes(text: str) -> bytes:
    voice = get_voice()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)
    return buf.getvalue()


def synthesize_stream_chunks(text: str):
    voice = get_voice()
    for chunk in voice.synthesize(text):
        yield chunk.audio_int16_bytes