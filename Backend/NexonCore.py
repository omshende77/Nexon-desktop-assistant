"""
NexonCore.py — Web orchestration engine for Nexon AI.

UPDATED:
  - Now uses Gemini exclusively via Backend.AIService
  - Supports real-time token streaming via WebSocket
  - Thread-aware conversation history (per thread_id)
  - Removed Groq and Cohere dependencies
  - Cleaner broadcast protocol with streaming tokens

WebSocket message protocol (Server → Client):
  { type: "status",    value: str }
  { type: "token",     content: str, thread_id: str }   ← new streaming
  { type: "message",   role: "assistant", content: str, thread_id: str }
  { type: "tts_ready", url: "/api/tts/audio" }
  { type: "images_ready", images: [...], prompt: str, navigate: "chat" }
  { type: "error",     message: str }
  { type: "exit" }
"""

import asyncio
import os
from typing import Callable, Awaitable
from dotenv import dotenv_values

from Backend.database.config import SessionLocal, DB_AVAILABLE
from Backend.database.services.message_service import MessageService
from Backend.database.services.conversation_service import ConversationService

env_vars      = dotenv_values(".env")
Username      = env_vars.get("Username",      "User")
Assistantname = env_vars.get("Assistantname", "Nexon")

# Task prefixes the DMM can return
TASK_FUNCTIONS = ["open", "close", "play", "system", "content", "youtube search"]


class NexonCore:
    """
    Async orchestration engine.
    
    Receives a text query + thread_id, routes through:
      Gemini DMM (classify) → Gemini Chat (stream) → edge-TTS → WebSocket broadcast
    """

    def __init__(self, broadcast_callback: Callable[[dict], Awaitable[None]]):
        self._broadcast      = broadcast_callback
        self.current_status: str = "Available..."
        self._processing: bool   = False

    # ── Broadcast helpers ─────────────────────────────────────────────────────

    async def broadcast(self, message: dict):
        """Send a message to all connected WebSocket clients."""
        if message.get("type") == "status":
            self.current_status = message["value"]
        try:
            await self._broadcast(message)
        except Exception as e:
            print(f"[NexonCore] Broadcast error: {e}")

    # ── TTS ───────────────────────────────────────────────────────────────────

    async def generate_tts(self, text: str):
        """Generate TTS audio with edge-tts and notify frontend to play it."""
        try:
            from Backend.TextToSpeech import TextToAudioFile
            await TextToAudioFile(text)
            await self.broadcast({"type": "tts_ready", "url": "/api/tts/audio"})
        except Exception as e:
            print(f"[TTS Error] {e}")

    # ── Main Query Processor ──────────────────────────────────────────────────

    async def process_query(
        self,
        query: str,
        username:      str = None,
        assistantname: str = None,
        thread_id:     str = "default",
        is_voice:      bool = False,
    ):
        """
        Full pipeline for a user message:
          1. Classify query with Gemini DMM
          2. Route to the appropriate handler (chat / realtime / automation / image)
          3. Stream Gemini tokens back to the frontend in real-time
          4. Generate TTS audio for the response
        """
        if self._processing:
            await self.broadcast({
                "type":    "info",
                "message": "Please wait for the current response to finish.",
            })
            return

        self._processing = True
        username      = username      or Username
        assistantname = assistantname or Assistantname

        try:
            # SAVE USER MESSAGE
            if DB_AVAILABLE and thread_id and thread_id != "default":
                try:
                    db = SessionLocal()
                    msg_service = MessageService()
                    msg_service.add_message(db, int(thread_id), "user", query)
                    db.close()
                except Exception as e:
                    print(f"[NexonCore DB] Error saving user msg: {e}")

            await self.broadcast({"type": "status", "value": "Thinking..."})

            loop = asyncio.get_event_loop()

            # ── Step 1: Classify the query ─────────────────────────────────
            from Backend.Model import FirstLayerDMM
            decision = await loop.run_in_executor(None, FirstLayerDMM, query)
            print(f"[NexonCore] Decision: {decision}")

            if not decision:
                decision = [f"general {query}"]

            G = any(i.startswith("general")  for i in decision)
            R = any(i.startswith("realtime") or i.startswith("google search") for i in decision)

            query_parts = []
            for i in decision:
                if i.startswith("general"):
                    query_parts.append(i.replace("general", "").strip())
                elif i.startswith("realtime"):
                    query_parts.append(i.replace("realtime", "").strip())
                elif i.startswith("google search"):
                    query_parts.append(i.replace("google search", "").strip())
                    
            merged_query = " and ".join(filter(bool, query_parts)) or query

            # ── Step 2: Image generation ───────────────────────────────────
            for q in decision:
                if q.startswith("generate image") or (
                    q.startswith("generate") and "image" in q
                ):
                    image_prompt = (
                        q.replace("generate image", "")
                         .replace("generate", "")
                         .strip()
                    )
                    if is_voice:
                        await self.broadcast({"type": "status", "value": "Speaking..."})
                        await self.generate_tts("Generating your image, let's head over to the chat section to see it.")
                    
                    await self.broadcast({"type": "status", "value": "Generating image..."})
                    try:
                        from Backend.ImageGeneration import GenerateImages
                        await loop.run_in_executor(None, GenerateImages, image_prompt)
                        safe = image_prompt.replace(" ", "_")
                        image_urls = [f"/data/{safe}1.jpg"]
                        
                        if DB_AVAILABLE and thread_id and thread_id != "default":
                            try:
                                db = SessionLocal()
                                msg_service = MessageService()
                                content = "Here is your generated image:\n\n" + "\n".join([f"![Image]({url})" for url in image_urls])
                                msg_service.add_message(db, int(thread_id), "assistant", content)
                                db.close()
                            except Exception as e:
                                pass

                        await self.broadcast({
                            "type":     "images_ready",
                            "images":   image_urls,
                            "prompt":   image_prompt,
                            "navigate": "chat",
                        })
                    except Exception as e:
                        print(f"[Image Gen Error] {e}")
                        await self.broadcast({
                            "type":    "error",
                            "message": f"Image generation failed: {str(e)}",
                        })
                    break

            # ── Step 3: Automation (desktop only) ─────────────────────────
            task_commands = [
                q for q in decision
                if any(q.startswith(f) for f in TASK_FUNCTIONS)
            ]
            if task_commands:
                await self.broadcast({"type": "status", "value": "Executing task..."})
                deployment_mode = os.environ.get("DEPLOYMENT_MODE", "local")
                try:
                    if deployment_mode == "local":
                        from Backend.Automation import Automation
                        await Automation(task_commands)
                        await self.broadcast({
                            "type":     "automation_result",
                            "success":  True,
                            "commands": task_commands,
                        })
                    else:
                        web_safe    = [q for q in task_commands if q.startswith(("google search", "youtube search"))]
                        desktop_only = [q for q in task_commands if q not in web_safe]
                        if web_safe:
                            from Backend.Automation import Automation
                            await Automation(web_safe)
                        if desktop_only:
                            await self.broadcast({
                                "type":    "automation_disabled",
                                "message": (
                                    f"Desktop automation unavailable in web mode: "
                                    f"{', '.join(desktop_only)}"
                                ),
                            })
                except Exception as e:
                    print(f"[Automation Error] {e}")
                    await self.broadcast({
                        "type":    "automation_result",
                        "success": False,
                        "error":   str(e),
                    })

            # ── Step 4: Generate text answer via Gemini (streaming) ────────
            answer = None

            if G or R:
                if R:
                    await self.broadcast({"type": "status", "value": "Searching the web..."})
                    from Backend.Search import get_realtime_search_results
                    loop = asyncio.get_event_loop()
                    web_data = await loop.run_in_executor(None, get_realtime_search_results, merged_query)
                    merged_query = f"User Query: {merged_query}\n\n{web_data}"

                await self.broadcast({"type": "status", "value": "Generating response..."})
                answer = await self._stream_gemini_response(
                    query=merged_query,
                    thread_id=thread_id,
                    username=username,
                    assistantname=assistantname,
                )

            else:
                # Walk decisions for edge cases
                for q in decision:
                    if q.startswith("general"):
                        await self.broadcast({"type": "status", "value": "Generating response..."})
                        qf = q.replace("general", "").strip() or query
                        answer = await self._stream_gemini_response(
                            query=qf,
                            thread_id=thread_id,
                            username=username,
                            assistantname=assistantname,
                        )
                        break
                    elif q.startswith("realtime") or q.startswith("google search"):
                        await self.broadcast({"type": "status", "value": "Searching the web..."})
                        qf = q.replace("realtime", "").replace("google search", "").strip() or query
                        from Backend.Search import get_realtime_search_results
                        loop = asyncio.get_event_loop()
                        web_data = await loop.run_in_executor(None, get_realtime_search_results, qf)
                        qf = f"User Query: {qf}\n\n{web_data}"
                        
                        answer = await self._stream_gemini_response(
                            query=qf,
                            thread_id=thread_id,
                            username=username,
                            assistantname=assistantname,
                        )
                        break
                    elif q.startswith("exit"):
                        answer = await self._stream_gemini_response(
                            query="Say a friendly goodbye as " + assistantname,
                            thread_id=thread_id,
                            username=username,
                            assistantname=assistantname,
                        )
                        await self.broadcast({"type": "exit"})
                        break

            # ── Step 5: TTS ────────────────────────────────────────────────
            if answer and is_voice:
                await self.broadcast({"type": "status", "value": "Speaking..."})
                # Strip markdown for cleaner TTS audio
                tts_text = _strip_markdown_for_tts(answer)
                await self.generate_tts(tts_text)

            await self.broadcast({"type": "status", "value": "Available..."})

        except Exception as e:
            print(f"[NexonCore Error] {e}")
            await self.broadcast({"type": "status",  "value":   "Available..."})
            await self.broadcast({"type": "error",   "message": f"An error occurred: {str(e)}"})

        finally:
            self._processing = False

    # ── Gemini streaming helper ───────────────────────────────────────────────

    async def _stream_gemini_response(
        self,
        query:         str,
        thread_id:     str,
        username:      str,
        assistantname: str,
    ) -> str:
        """
        Stream Gemini tokens via WebSocket, then send the full message at end.
        Handles Groq fallback automatically.
        """
        from Backend.AIService import stream_chat_response

        full_response = ""
        token_count   = 0
        current_provider = "Google Gemini"

        try:
            async for token in stream_chat_response(
                query=query,
                thread_id=thread_id,
                username=username,
                assistantname=assistantname,
            ):
                if token == "[FALLBACK_TRIGGERED]":
                    current_provider = "Gemini (Fallback)"
                    await self.broadcast({
                        "type": "info",
                        "message": "Groq failed. Switching to Gemini fallback..."
                    })
                    continue

                full_response += token
                token_count   += 1
                await self.broadcast({
                    "type":      "token",
                    "content":   token,
                    "thread_id": thread_id,
                })

        except Exception as e:
            print(f"[NexonCore] Stream error: {e}")
            full_response = f"I encountered an error generating a response: {str(e)}"

        if full_response:
            # SAVE ASSISTANT MESSAGE
            if DB_AVAILABLE and thread_id and thread_id != "default":
                try:
                    db = SessionLocal()
                    msg_service = MessageService()
                    msg_service.add_message(db, int(thread_id), "assistant", full_response)
                    db.close()
                except Exception as e:
                    print(f"[NexonCore DB] Error saving assistant msg: {e}")

            await self.broadcast({
                "type":        "message",
                "role":        "assistant",
                "content":     full_response,
                "thread_id":   thread_id,
                "ai_provider": current_provider,
            })

        return full_response


# ── Utility ───────────────────────────────────────────────────────────────────

def _strip_markdown_for_tts(text: str) -> str:
    """
    Remove markdown syntax before sending to TTS.
    Keeps the text natural-sounding when spoken aloud.
    """
    import re
    # Remove code blocks entirely (don't speak raw code)
    text = re.sub(r"```[\s\S]*?```", "code block omitted", text)
    text = re.sub(r"`[^`]+`", "", text)
    # Remove headers
    text = re.sub(r"#{1,6}\s+", "", text)
    # Remove bold/italic
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    # Remove links
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove bullet points
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    # Remove numbered lists markers
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    # Collapse multiple whitespace/newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    
    # Truncate if too long (more than 12 sentences) to prevent endless talking
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
    # Filter out empty strings from the split
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) > 12:
        text = " ".join(sentences[:12]).strip()
        text += " You can check the remaining in the chats section."
        
    return text
