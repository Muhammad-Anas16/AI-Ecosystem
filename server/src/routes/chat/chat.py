from fastapi import APIRouter
from pydantic import BaseModel

from server.src.controllers import chatController

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    api_key: str


@router.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    return chatController.handle_chat_stream(req.message, req.api_key)