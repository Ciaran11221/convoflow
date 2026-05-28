import os
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Generator

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Standard (non-streaming) response — kept for testing/fallback
def get_chat_response(messages: list) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system="You are a helpful AI assistant.",
        messages=messages
    )
    return response.content[0].text


# Streaming response — yields tokens as they arrive from Claude
def stream_chat_response(messages: list) -> Generator[str, None, None]:
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system="You are a helpful AI assistant.",
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            yield text