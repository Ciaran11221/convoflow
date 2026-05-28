import os
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Generator
from tools import TOOLS, execute_tool
from memory import store_turn, retrieve_context

load_dotenv()

# Haiku for tool calls (cost efficient), Sonnet for main chat
CHAT_MODEL = "claude-sonnet-4-5"
TOOL_MODEL = "claude-haiku-4-5-20251001"

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def build_system_prompt(query: str, session_id: str) -> str:
    """
    Builds the system prompt, injecting relevant past context
    from ChromaDB if any exists for this session.
    """
    base = "You are a helpful AI assistant. Use tools when appropriate."

    context = retrieve_context(query, session_id)
    if not context:
        return base

    return f"""{base}

## Relevant past context from this conversation:
{context}

Use this context only if relevant. Do not mention it explicitly unless asked."""


def get_chat_response(messages: list, session_id: str = "default") -> str:
    """
    Sends messages to Claude with memory-injected system prompt.
    Handles the agentic tool use loop until Claude gives a final answer.
    Stores the completed turn in ChromaDB.
    """
    user_message = messages[-1]["content"]
    system = build_system_prompt(user_message, session_id)

    response = client.messages.create(
        model=TOOL_MODEL,
        max_tokens=1024,
        system=system,
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

        messages = messages + [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results}
        ]

        response = client.messages.create(
            model=TOOL_MODEL,
            max_tokens=1024,
            system=system,
            tools=TOOLS,
            messages=messages
        )

    reply = response.content[0].text

    # Store this turn in memory for future retrieval
    store_turn(session_id, user_message, reply)

    return reply


def stream_chat_response(messages: list) -> Generator[str, None, None]:
    """
    Streams Claude's response token by token.
    Used for regular conversation without tool use.
    """
    with client.messages.stream(
        model=CHAT_MODEL,
        max_tokens=1024,
        system="You are a helpful AI assistant.",
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            yield text