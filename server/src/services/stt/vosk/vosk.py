import zipfile
import urllib.request
from pathlib import Path

from vosk import Model, KaldiRecognizer

MODEL_NAME = "vosk-model-small-en-us-0.15"
MODEL_URL = f"https://alphacephei.com/vosk/models/{MODEL_NAME}.zip"

BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "model"
ZIP_PATH = BASE_DIR / f"{MODEL_NAME}.zip"

_model = None


def _download_and_extract():
    print("[STT-Vosk] Model pehli baar download ho rahi hai (~40MB)...")
    urllib.request.urlretrieve(MODEL_URL, ZIP_PATH)

    print("[STT-Vosk] Extract ho rahi hai...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(BASE_DIR)

    extracted_folder = BASE_DIR / MODEL_NAME
    if extracted_folder.exists():
        extracted_folder.rename(MODEL_DIR)

    ZIP_PATH.unlink(missing_ok=True)
    print("[STT-Vosk] Model ready.")


def ensure_downloaded():
    if not MODEL_DIR.exists() or not any(MODEL_DIR.iterdir()):
        _download_and_extract()


def get_model():
    global _model
    if _model is None:
        ensure_downloaded()
        _model = Model(str(MODEL_DIR))
    return _model


def new_recognizer(sample_rate: int = 16000) -> KaldiRecognizer:
    return KaldiRecognizer(get_model(), sample_rate)