import json

from server.src.services.stt.vosk.vosk import new_recognizer as new_vosk_recognizer
from server.src.services.stt.google.google import GoogleStreamSession
from server.src.services.llm.google.google import stream_gemini_response
from server.src.services.tts.piper.piper import synthesize_to_wav_bytes, synthesize_stream_chunks


def make_recognizer(provider: str, sample_rate: int = 16000):
    if provider == "vosk":
        return {"type": "vosk", "engine": new_vosk_recognizer(sample_rate)}
    return {"type": "google", "engine": GoogleStreamSession(sample_rate)}


def process_audio_chunk(recognizer_obj, chunk: bytes):
    if recognizer_obj["type"] == "vosk":
        engine = recognizer_obj["engine"]
        if engine.AcceptWaveform(chunk):
            result = json.loads(engine.Result())
            return result.get("text", ""), None
        partial = json.loads(engine.PartialResult())
        return None, partial.get("partial", "")

    engine = recognizer_obj["engine"]
    engine.add_chunk(chunk)
    if engine.should_finalize():
        return engine.finalize(), None
    return None, None


def get_tts_wav(text: str) -> bytes:
    return synthesize_to_wav_bytes(text)


def get_tts_stream(text: str):
    return synthesize_stream_chunks(text)


def get_llm_stream(message: str, api_key: str):
    return stream_gemini_response(message, api_key)