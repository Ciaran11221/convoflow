import os
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Generator
from tools import TOOLS, execute_tool

load_dotenv()

# Use Haiku for tool calls (cheaper), Sonnet for main chat
CHAT_MODEL = "claude-sonnet-4-5"
TOOL_MODEL = "claude-haiku-4-5-20251001"

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = "You are a helpful AI assistant. Use tools when appropriate."


def get_chat_response(messages: list) -> str:
    """
    Sends messages to Claude. If Claude decides to use a tool,
    we execute it and feed the result back — this loops until
    Claude gives a final text response.
    """
    response = client.messages.create(
        model=TOOL_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages
    )

    # Agentic loop — keep going until Claude stops calling tools
    while response.stop_reason == "tool_use":
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # Send tool results back to Claude for its final answer
        messages = messages + [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results}
        ]

        response = client.messages.create(
            model=TOOL_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

    return response.content[0].text


def stream_chat_response(messages: list) -> Generator[str, None, None]:
    """
    Streams Claude's response token by token.
    Note: streaming doesn't support tool use, so this is used
    for regular conversation without tools.
    """
    with client.messages.stream(
        model=CHAT_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            yield text