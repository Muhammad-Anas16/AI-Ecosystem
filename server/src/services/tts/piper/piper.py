import os
import io
import wave

from piper import PiperVoice

VOICE_PATH = os.path.join(os.path.dirname(__file__), "voices", "en_US-lessac-medium.onnx")

_voice = None


def get_voice():
    global _voice
    if _voice is None:
        if not os.path.exists(VOICE_PATH):
            raise RuntimeError(
                "Piper voice nahi mili. Terminal mein chalao:\n"
                "python -m piper.download_voices en_US-lessac-medium\n"
                "Phir .onnx aur .onnx.json files server/src/services/tts/piper/voices/ mein daalo."
            )
        _voice = PiperVoice.load(VOICE_PATH)
    return _voice


def synthesize_to_wav_bytes(text: str) -> bytes:
    """Poora WAV file — Postman mein seedha play/preview hota hai."""
    voice = get_voice()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)
    return buf.getvalue()


def synthesize_stream_chunks(text: str):
    """Real-time — audio ready hote hi chunk yield hota hai, poora wait nahi karna."""
    voice = get_voice()
    for chunk in voice.synthesize(text):
        yield chunk.audio_int16_bytes