import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.src.config.config import HOST, PORT
from server.src.routes.chat import chat
from server.src.routes.voice import voice
from server.src.services.stt.vosk.vosk import ensure_downloaded as ensure_vosk_model
from server.src.services.tts.piper.piper import ensure_downloaded as ensure_piper_voice

app = FastAPI(title="AI-Ecosystem Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(voice.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Server is alive"}


@app.on_event("startup")
async def on_startup():
    print("Starting AI Engine...")
    print("Checking Models...")
    ensure_vosk_model()
    ensure_piper_voice()
    print("AI Ready")


if __name__ == "__main__":
    uvicorn.run("server.main:app", host=HOST, port=PORT, reload=True)