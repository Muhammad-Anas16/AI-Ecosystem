from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Response
from pydantic import BaseModel

from server.src.controllers import voiceController

router = APIRouter()


@router.websocket("/api/voice/stt/vosk")
async def stt_vosk(websocket: WebSocket):
    await websocket.accept()
    recognizer_obj = voiceController.make_recognizer("vosk")

    try:
        while True:
            chunk = await websocket.receive_bytes()
            final_text, partial_text = voiceController.process_audio_chunk(recognizer_obj, chunk)
            if final_text is not None:
                await websocket.send_json({"final": True, "text": final_text})
            elif partial_text is not None:
                await websocket.send_json({"final": False, "text": partial_text})
    except WebSocketDisconnect:
        pass


@router.websocket("/api/voice/stt/google")
async def stt_google(websocket: WebSocket):
    await websocket.accept()
    recognizer_obj = voiceController.make_recognizer("google")

    try:
        while True:
            chunk = await websocket.receive_bytes()
            final_text, _ = voiceController.process_audio_chunk(recognizer_obj, chunk)
            if final_text is not None:
                await websocket.send_json({"final": True, "text": final_text})
    except WebSocketDisconnect:
        pass


class TTSRequest(BaseModel):
    text: str


@router.post("/api/voice/tts")
async def text_to_speech(req: TTSRequest):
    wav_bytes = voiceController.get_tts_wav(req.text)
    return Response(content=wav_bytes, media_type="audio/wav")


@router.websocket("/api/voice/pipeline")
async def voice_pipeline(websocket: WebSocket, stt: str = "vosk", api_key: str = ""):
    await websocket.accept()

    if not api_key:
        await websocket.send_json({"type": "error", "text": "api_key query param zaroori hai"})
        await websocket.close()
        return

    recognizer_obj = voiceController.make_recognizer(stt)

    try:
        while True:
            chunk = await websocket.receive_bytes()
            final_text, partial_text = voiceController.process_audio_chunk(recognizer_obj, chunk)

            if partial_text is not None:
                await websocket.send_json({"type": "partial_text", "text": partial_text})

            if final_text:
                await websocket.send_json({"type": "user_text", "text": final_text})

                full_reply = ""
                for piece in voiceController.get_llm_stream(final_text, api_key):
                    full_reply += piece
                    await websocket.send_json({"type": "llm_chunk", "text": piece})

                await websocket.send_json({"type": "llm_done", "text": full_reply})

                for audio_chunk in voiceController.get_tts_stream(full_reply):
                    await websocket.send_bytes(audio_chunk)

                await websocket.send_json({"type": "audio_done"})
    except WebSocketDisconnect:
        pass