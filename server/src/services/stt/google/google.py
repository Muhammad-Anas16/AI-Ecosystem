import array
import io
import math
import wave

import speech_recognition as sr

recognizer = sr.Recognizer()

SILENCE_THRESHOLD = 300           # is RMS se neeche "khaamoshi" maana jata hai
SILENCE_CHUNKS_TO_FINALIZE = 12   # itni der khaamoshi ke baad utterance khatam maano


def _rms(pcm_bytes: bytes) -> float:
    samples = array.array('h', pcm_bytes)  # 16-bit signed samples
    if len(samples) == 0:
        return 0.0
    return math.sqrt(sum(s * s for s in samples) / len(samples))


def _pcm_to_wav_bytes(pcm_bytes: bytes, sample_rate: int) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()


def transcribe_pcm(pcm_bytes: bytes, sample_rate: int = 16000) -> str:
    wav_bytes = _pcm_to_wav_bytes(pcm_bytes, sample_rate)
    with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data, language="en-US")
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"(Google STT error: {e})"


class GoogleStreamSession:
    """
    Har WebSocket connection ka apna session — Vosk ki tarah built-in streaming
    Google ke free API mein nahi hoti, isliye humne khud chhota sa silence-detector
    (VAD) banaya hai: jab tak bol rahe ho buffer collect hota hai, pause hote hi
    Google ko bhej kar text nikalta hai. Yehi is provider ka "real-time" hai.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.buffer = bytearray()
        self.silence_chunks = 0
        self.has_speech = False

    def add_chunk(self, chunk: bytes):
        self.buffer.extend(chunk)
        if _rms(chunk) > SILENCE_THRESHOLD:
            self.has_speech = True
            self.silence_chunks = 0
        else:
            self.silence_chunks += 1

    def should_finalize(self) -> bool:
        return self.has_speech and self.silence_chunks >= SILENCE_CHUNKS_TO_FINALIZE

    def finalize(self) -> str:
        pcm_bytes = bytes(self.buffer)
        self.buffer = bytearray()
        self.has_speech = False
        self.silence_chunks = 0
        return transcribe_pcm(pcm_bytes, self.sample_rate) if pcm_bytes else ""