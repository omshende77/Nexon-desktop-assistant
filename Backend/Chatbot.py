"""
Chatbot.py — Gemini-powered chat response generator.

MIGRATION NOTE:
  Previously used Groq (LLaMA 3.3 70B).
  Now uses Gemini via the centralized AIService layer.
  To swap models again, edit Backend/AIService.py → MODEL_NAME only.

Public API (unchanged, preserving backward compatibility):
  ChatBot(Query)            — synchronous, returns full answer string
  ChatBotStream(Query, thread_id) — async generator, yields tokens
"""

import asyncio
from dotenv import dotenv_values
from Backend.AIService import (
    stream_chat_response,
    get_chat_response,
    append_to_thread,
    get_thread_history,
    clear_thread_history,
    load_thread_history_from_messages,
    classify_query,
    ASSISTANT_NAME,
    USERNAME,
)

env_vars = dotenv_values(".env")
Username      = env_vars.get("Username",      USERNAME)
Assistantname = env_vars.get("Assistantname", ASSISTANT_NAME)

# Default thread for legacy synchronous callers (desktop app compat)
_DEFAULT_THREAD = "default"


def ChatBot(Query: str, thread_id: str = _DEFAULT_THREAD) -> str:
    """
    Synchronous chat — blocks until Gemini returns the full response.
    
    Preserves backward-compatible interface for any code that calls ChatBot().
    Internally uses Gemini via AIService.
    """
    try:
        return asyncio.run(_async_chatbot(Query, thread_id))
    except RuntimeError:
        # Already inside an event loop (e.g., called from FastAPI)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_async_chatbot(Query, thread_id))


async def _async_chatbot(Query: str, thread_id: str) -> str:
    """Internal async wrapper."""
    return await get_chat_response(
        query=Query,
        thread_id=thread_id,
        username=Username,
        assistantname=Assistantname,
    )


async def ChatBotStream(Query: str, thread_id: str = _DEFAULT_THREAD):
    """
    Async generator — yields Gemini response tokens one by one.
    
    Usage:
        async for token in ChatBotStream(query, thread_id):
            await ws.send_json({"type": "token", "content": token})
    """
    async for token in stream_chat_response(
        query=Query,
        thread_id=thread_id,
        username=Username,
        assistantname=Assistantname,
    ):
        yield token


# Re-export history helpers for convenience
__all__ = [
    "ChatBot",
    "ChatBotStream",
    "append_to_thread",
    "get_thread_history",
    "clear_thread_history",
    "load_thread_history_from_messages",
]


if __name__ == "__main__":
    print(f"Nexon AI Chatbot — powered by Gemini")
    print(f"Assistant: {Assistantname} | User: {Username}")
    print("Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit", "bye"):
            break
        if user_input:
            answer = ChatBot(user_input)
            print(f"{Assistantname}: {answer}\n")
