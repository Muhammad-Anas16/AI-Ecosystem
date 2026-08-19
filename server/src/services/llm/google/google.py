from google import genai


def stream_gemini_response(message: str, api_key: str):
    """Real-time — chunks aate hi yield karta hai."""
    client = genai.Client(api_key=api_key)
    stream = client.models.generate_content_stream(
        model="gemini-3.5-flash",
        contents=message,
    )
    for chunk in stream:
        if chunk.text:
            yield chunk.text