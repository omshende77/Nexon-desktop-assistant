"""
AIService.py — Centralized AI service layer for Nexon AI.

Dynamic Model Routing:
- Primary Provider: Groq (llama-3.3-70b-versatile) — extremely fast, no quota issues.
- Fallback Provider: Google Gemini — used if Groq is unavailable.
"""

import asyncio
import os
from typing import AsyncGenerator
from dotenv import dotenv_values

from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
import google.generativeai as genai

try:
    from groq import Groq
    GROQ_AVAILABLE = True
    print("GROQ IMPORT SUCCESS")
except Exception as e:
    print("GROQ IMPORT ERROR:", e)
    GROQ_AVAILABLE = False

# ── Configuration ─────────────────────────────────────────────────────────────

env_vars = dotenv_values(".env")

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    env_vars.get("GEMINI_API_KEY", "")
)

GROQ_API_KEY = os.getenv(
    "GroqAPIKey",
    env_vars.get("GroqAPIKey", "")
)

USERNAME = os.getenv(
    "Username",
    env_vars.get("Username", "User")
)

ASSISTANT_NAME = os.getenv(
    "Assistantname",
    env_vars.get("Assistantname", "Nexon")
)

# Models
GROQ_MODEL_NAME       = "llama-3.1-8b-instant"
GEMINI_MODEL_NAME     = "gemini-2.0-flash"

# ── Prompts ───────────────────────────────────────────────────────────────────

import datetime

def RealtimeInformation():
    now = datetime.datetime.now()
    return f"""
    Current Real-time Information:
    - Day: {now.strftime("%A")}
    - Date: {now.strftime("%d")}
    - Month: {now.strftime("%B")}
    - Year: {now.strftime("%Y")}
    - Time: {now.strftime("%H:%M:%S")}
    """

def get_system_prompt():
    return f"""You are {ASSISTANT_NAME}, a highly capable and friendly AI assistant created for {USERNAME}.

Your personality:
- Concise, accurate, and helpful
- Natural conversational tone
- Never mention your training data or cutoff dates
- Reply in English only
- Do not add unnecessary preamble or disclaimers

Important rules:
- Keep responses focused and appropriately detailed
- Use markdown formatting for code blocks, lists, and structure when helpful
- Never say "I cannot" without offering an alternative
- Maintain context from the full conversation history
- You have access to real-time clock. When asked for time/date, answer directly using this data:

{RealtimeInformation()}
"""

DMM_PROMPT = """You are a command and intent classifier for an AI assistant.

Your task is to convert the user's request into one or more executable commands.

Return ONLY the command(s).
Do NOT explain.
Do NOT use markdown.
Do NOT add extra text.
Do NOT return placeholders such as <song>, <app>, <query>, <task>, or <prompt>.

Available commands:

* general <query>
  Use for normal questions that can be answered directly.

* realtime <query>
  Use when current/live information is required.

* generate image <prompt>
  Use when the user wants an image created.

* open <app/site>
  Open an application or website.

* close <app>
  Close an application.

* play <song name>
  Play the exact song, artist, album, playlist, or music request specified by the user.

* system <task>
  System actions such as:
  volume up
  volume down
  mute
  unmute
  pause
  resume

* google search <query>
  Search Google.

* youtube search <query>
  Search YouTube.

* exit
  User wants to end the conversation.

Rules:

1. Always preserve the user's original request.
2. Never replace user content with generic placeholders.
3. Never output <song>, <app>, <query>, <task>, or any template text.
4. For music requests, include the exact requested music.
5. For application requests, include the exact application name.
6. Multiple commands must be separated by commas.
7. Output commands only.

Examples:

User: Play Bangles songs
Output:
play Bangles songs

User: Play Kesariya
Output:
play Kesariya

User: Play Arijit Singh songs
Output:
play Arijit Singh songs

User: Open Chrome
Output:
open chrome

User: Open YouTube and play Believer
Output:
open youtube, play Believer

User: Search Python FastAPI tutorial
Output:
google search Python FastAPI tutorial

User: Find today's weather in Pune
Output:
realtime weather in Pune today

User: Increase volume
Output:
system volume up

User: Bye
Output:
exit

If the request does not match any command category, return:

general <original user request>

"""

# ── Clients Init ──────────────────────────────────────────────────────────────

def _init_clients():
    print("GROQ AVAILABLE:", GROQ_AVAILABLE)
    print("GROQ KEY FOUND:", bool(GROQ_API_KEY))
    print("GROQ MODEL:", GROQ_MODEL_NAME)
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    
    global groq_client
    groq_client = None
    if GROQ_AVAILABLE and GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)

_init_clients()

# ── Thread History Store ──────────────────────────────────────────────────────

_thread_histories: dict[str, list[dict]] = {}

def _user_thread_key(username: str, thread_id: str) -> str:
    """Combine username and thread_id to create a unique key for storing history per user."""
    return f"{username}:{thread_id}"

def get_thread_history(thread_id: str, username: str) -> list[dict]:
    key = _user_thread_key(username, thread_id)
    return _thread_histories.get(key, [])

def append_to_thread(thread_id: str, username: str, role: str, text: str):
    key = _user_thread_key(username, thread_id)
    if key not in _thread_histories:
        _thread_histories[key] = []
    _thread_histories[key].append({
        "role": role,
        "parts": [{"text": text}],
    })
    return


def clear_thread_history(thread_id: str, username: str):
    key = _user_thread_key(username, thread_id)
    _thread_histories.pop(key, None)

def load_thread_history_from_messages(thread_id: str, username: str, messages: list[dict]):
    key = _user_thread_key(username, thread_id)
    history = []
    for msg in messages:
        gemini_role = "user" if msg.get("role") == "user" else "model"
        content = msg.get("content", "")
        if content:
            history.append({
                "role": gemini_role,
                "parts": [{"text": content}],
            })
    _thread_histories[key] = history

def _history_to_groq_format(gemini_history: list[dict]) -> list[dict]:
    groq_hist = []
    for msg in gemini_history:
        role = "assistant" if msg["role"] == "model" else "user"
        text = msg["parts"][0]["text"]
        groq_hist.append({"role": role, "content": text})
    return groq_hist

# ── Groq Only ─────────────────────────────────────────────────────────────────

# ── Core: Streaming Chat ──────────────────────────────────────────────────────

async def stream_chat_response(
    query: str,
    thread_id: str,
    username: str = None,
    assistantname: str = None,
) -> AsyncGenerator[str, None]:
    if not groq_client:
        yield "⚠️ Groq is not configured. Please check your GroqAPIKey in the .env file."
        return

    append_to_thread(thread_id, username, "user", query)
    history = get_thread_history(thread_id, username)
    chat_history = history[:-1] if len(history) > 1 else []

    groq_messages = [{"role": "system", "content": get_system_prompt()}] + _history_to_groq_format(chat_history)
    groq_messages.append({"role": "user", "content": query})

    try:
        completion = await asyncio.to_thread(
            lambda: groq_client.chat.completions.create(
                model=GROQ_MODEL_NAME,
                messages=groq_messages,
                max_tokens=2048,
                temperature=0.7,
                stream=True,
            )
        )

        full_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                yield text

        if full_response:
            append_to_thread(thread_id, username, "model", full_response)

    except Exception as e:
        print(f"[AIService] Groq stream failed: {e}")
        yield f"⚠️ Error generating response: {str(e)}"

async def get_chat_response(query: str, thread_id: str) -> str:
    full = ""
    async for chunk in stream_chat_response(query, thread_id):
        if chunk != "[FALLBACK_TRIGGERED]":
            full += chunk
    return full

# ── Decision-Making Model ─────────────────────────────────────────────────────

def classify_query(query: str) -> list[str]:
    # Try Groq first
    if groq_client:
        try:
            completion = groq_client.chat.completions.create(
                model=GROQ_MODEL_NAME,
                messages=[
                    {"role": "system", "content": DMM_PROMPT},
                    {"role": "user", "content": query}
                ],
                max_tokens=256,
                temperature=0.1,
            )
            raw = completion.choices[0].message.content.strip().replace("\n", "")
            print("[DMM RAW]", raw)
            return _parse_dmm_output(raw, query)
        except Exception as e:
            print(f"[AIService] DMM Groq failed ({e}), falling back to Gemini.")
            pass
            
    # Fallback to Gemini
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel(
                model_name=GEMINI_MODEL_NAME,
                system_instruction=DMM_PROMPT,
            )
            response = model.generate_content(query)
            raw = response.text.strip().replace("\n", "")
            return _parse_dmm_output(raw, query)
        except Exception as e:
            print(f"[AIService] DMM Gemini fallback error: {e}")
            pass

    return [f"general {query}"]

def _parse_dmm_output(raw: str, original_query: str) -> list[str]:
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    valid_prefixes = [
        "general", "realtime", "generate image", "open", "close",
        "play", "system", "content", "google search", "youtube search", "exit", "reminder"
    ]
    filtered = [p for p in parts if any(p.lower().startswith(pf) for pf in valid_prefixes)]
    if not filtered:
        return [f"general {original_query}"]
    return filtered

async def health_check() -> dict:
    if groq_client:
        return {"status": "ok", "model": GROQ_MODEL_NAME, "response": "Using Groq primary"}
    elif GEMINI_API_KEY:
        return {"status": "ok", "model": GEMINI_MODEL_NAME, "response": "Using Gemini fallback"}
    return {"status": "error", "error": "No AI providers configured"}
