import os
from vosk import Model, KaldiRecognizer

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model")

_model = None


def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH) or not os.listdir(MODEL_PATH):
            raise RuntimeError(
                "Vosk model nahi mili. https://alphacephei.com/vosk/models se "
                "'vosk-model-small-en-us-0.15' download karke "
                "server/src/services/stt/vosk/model/ mein daalo."
            )
        _model = Model(MODEL_PATH)
    return _model


def new_recognizer(sample_rate: int = 16000) -> KaldiRecognizer:
    return KaldiRecognizer(get_model(), sample_rate)