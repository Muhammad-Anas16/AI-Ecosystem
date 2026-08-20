from fastapi.responses import StreamingResponse

from server.src.services.llm.google.google import stream_gemini_response


def handle_chat_stream(message: str, api_key: str):
    if not api_key:
        def error_gen():
            yield "Error: API key missing hai."
        return StreamingResponse(error_gen(), media_type="text/plain")

    return StreamingResponse(
        stream_gemini_response(message, api_key),
        media_type="text/plain"
    )