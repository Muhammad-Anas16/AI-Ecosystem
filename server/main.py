import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.src.config.config import HOST, PORT
from server.src.routes.chat import chat
from server.src.routes.voice import voice

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


if __name__ == "__main__":
    uvicorn.run("server.main:app", host=HOST, port=PORT, reload=True)