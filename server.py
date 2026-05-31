"""
server.py — FastAPI backend for Nexon AI Web.

UPDATED:
  - Thread-aware WebSocket routing (thread_id passed in query messages)
  - Gemini health check endpoint (/api/ai/health)
  - Streaming token events supported (type: "token")
  - Thread history sync endpoint (/api/thread/sync)
  - Clean separation between desktop and web modes

Run:
    uvicorn server:app --reload --port 8000

Then run the React frontend:
    cd nexon-ui && npm run dev
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Set

from Backend.database.init_db import init_database
from Backend.database.config import get_db, DB_AVAILABLE
from Backend.database.services.conversation_service import ConversationService
from Backend.database.services.message_service import MessageService
from fastapi import Depends
from sqlalchemy.orm import Session

import uvicorn
from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── Environment ───────────────────────────────────────────────────────────────

env_vars      = dotenv_values(".env")
Username      = env_vars.get("Username",      "User")
Assistantname = env_vars.get("Assistantname", "Nexon")
DEPLOYMENT_MODE = os.environ.get("DEPLOYMENT_MODE", "local")

# ── FastAPI App ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Nexon AI API",
    description="FastAPI backend for the Nexon AI web interface — powered by Gemini",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from Backend.auth_routes import router as auth_router, get_current_user
from Backend.api_routes.data_routes import router as data_router
from Backend.database.models import User
app.include_router(auth_router)
app.include_router(data_router)

# ── Static File Mounts ────────────────────────────────────────────────────────

GRAPHICS_DIR = Path("Frontend/Graphics")
DATA_DIR     = Path("Data")
REACT_BUILD  = Path("nexon-ui/dist")

if GRAPHICS_DIR.exists():
    app.mount("/graphics", StaticFiles(directory=str(GRAPHICS_DIR)), name="graphics")

if DATA_DIR.exists():
    app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

# ── WebSocket Connection Manager ──────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        dead: Set[WebSocket] = set()
        for ws in list(self.active_connections):
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        self.active_connections -= dead


manager = ConnectionManager()

# ── NexonCore ─────────────────────────────────────────────────────────────────

from Backend.NexonCore import NexonCore
nexon = NexonCore(broadcast_callback=manager.broadcast)

# ── Pydantic Models ───────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    text:      str
    thread_id: str = "default"


class ThreadSyncRequest(BaseModel):
    thread_id: str
    messages:  list  # list of { role, content }

class ConversationCreateRequest(BaseModel):
    title: str = "New Chat"

class ConversationUpdateRequest(BaseModel):
    title: str

class MessageCreateRequest(BaseModel):
    role: str
    content: str
    message_type: str = "text"


# ── REST Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status":               "ok",
        "assistant":            Assistantname,
        "username":             Username,
        "ai_provider":          "Google Gemini",
        "deployment_mode":      DEPLOYMENT_MODE,
        "automation_available": DEPLOYMENT_MODE == "local",
    }


@app.get("/api/config")
async def get_config():
    return {
        "username":             Username,
        "assistantname":        Assistantname,
        "deployment_mode":      DEPLOYMENT_MODE,
        "automation_available": DEPLOYMENT_MODE == "local",
        "ai_provider":          "Google Gemini",
    }


@app.get("/api/ai/health")
async def ai_health():
    """Check Gemini API connectivity."""
    from Backend.AIService import health_check
    result = await health_check()
    status_code = 200 if result["status"] == "ok" else 503
    return JSONResponse(content=result, status_code=status_code)


@app.post("/api/thread/sync")
async def sync_thread_history(req: ThreadSyncRequest):
    """
    Sync frontend thread message history to backend Gemini context.
    Called when a user switches to an existing thread so Gemini
    has the full conversation context.
    """
    try:
        from Backend.AIService import load_thread_history_from_messages
        load_thread_history_from_messages(req.thread_id, "default", req.messages)
        return {"status": "ok", "thread_id": req.thread_id, "synced": len(req.messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/thread/{thread_id}")
async def delete_thread_history(thread_id: str):
    """Clear Gemini conversation history for a thread."""
    from Backend.AIService import clear_thread_history
    clear_thread_history(thread_id)
    return {"status": "ok", "thread_id": thread_id}


@app.post("/api/chat/send")
async def send_message_rest(req: QueryRequest, current_user: User = Depends(get_current_user)):
    """REST fallback for sending a message (WebSocket preferred)."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty message")
    asyncio.create_task(
        nexon.process_query(req.text, current_user.username, Assistantname, req.thread_id, user_id=current_user.id)
    )
    return {"status": "processing", "message": req.text, "thread_id": req.thread_id}


@app.get("/api/tts/audio")
async def get_tts_audio():
    """Serve the most recently generated TTS MP3 file."""
    audio_path = DATA_DIR / "speech.mp3"
    if audio_path.exists():
        return FileResponse(
            str(audio_path),
            media_type="audio/mpeg",
            headers={"Cache-Control": "no-store"},
        )
    raise HTTPException(status_code=404, detail="No TTS audio available yet")


@app.get("/api/status")
async def get_status():
    return {
        "status":          nexon.current_status,
        "is_processing":   nexon._processing,
        "deployment_mode": DEPLOYMENT_MODE,
        "db_available":    DB_AVAILABLE
    }

# ── Database Endpoints ────────────────────────────────────────────────────────

@app.get("/api/users/{user_id}/conversations")
def get_conversations(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not DB_AVAILABLE:
        return {"conversations": [], "status": "ephemeral"}
    service = ConversationService()
    convos = service.get_all_conversations(db, current_user.id)
    return {"conversations": [{"id": c.id, "title": c.title, "created_at": c.created_at, "updated_at": c.updated_at} for c in convos], "status": "persistent"}

@app.post("/api/users/{user_id}/conversations")
def create_conversation(user_id: int, req: ConversationCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not DB_AVAILABLE:
        return {"id": "default", "title": req.title, "status": "ephemeral"}
    service = ConversationService()
    c = service.create_conversation(db, req.title, current_user.id)
    return {"id": c.id, "title": c.title, "created_at": c.created_at, "updated_at": c.updated_at}

@app.get("/api/users/{user_id}/conversations/{conversation_id}/messages")
def get_conversation_messages(user_id: int, conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not DB_AVAILABLE or conversation_id == "default":
        return {"messages": [], "status": "ephemeral"}
        
    conv_service = ConversationService()
    conv = conv_service.get_conversation(db, int(conversation_id), current_user.id)
    if not conv:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
        
    service = MessageService()
    msgs = service.get_conversation_history(db, int(conversation_id))
    return {"messages": [{"id": m.id, "role": m.role, "content": m.content, "type": m.message_type, "created_at": m.created_at} for m in msgs], "status": "persistent"}

@app.put("/api/users/{user_id}/conversations/{conversation_id}")
def update_conversation(user_id: int, conversation_id: str, req: ConversationUpdateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not DB_AVAILABLE or conversation_id == "default":
        return {"status": "ephemeral"}
    service = ConversationService()
    c = service.update_title(db, int(conversation_id), req.title, current_user.id)
    return {"id": c.id, "title": c.title, "updated_at": c.updated_at}

@app.delete("/api/users/{user_id}/conversations/{conversation_id}")
def delete_conversation(user_id: int, conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not DB_AVAILABLE or conversation_id == "default":
        return {"status": "ephemeral"}
    service = ConversationService()
    service.delete_conversation(db, int(conversation_id), current_user.id)
    from Backend.AIService import clear_thread_history
    clear_thread_history(str(conversation_id), current_user.username)
    return {"status": "deleted", "id": conversation_id}


# ── WebSocket Endpoint ────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)

    # Initial handshake
    try:
        await websocket.send_json({
            "type":                 "init",
            "username":             Username,
            "assistantname":        Assistantname,
            "deployment_mode":      DEPLOYMENT_MODE,
            "automation_available": DEPLOYMENT_MODE == "local",
            "ai_provider":          "Google Gemini",
        })
    except Exception as e:
        print(f"[WS] Init error: {e}")

    authenticated_user = None

    try:
        while True:
            data     = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "auth":
                token = data.get("token")
                try:
                    from jose import jwt
                    from Backend.database.services.auth_service import SECRET_KEY, ALGORITHM, get_user
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    username = payload.get("sub")
                    if username:
                        user = get_user(db, username=username)
                        if user:
                            authenticated_user = user
                            await websocket.send_json({"type": "auth_success", "username": username})
                        else:
                            await websocket.send_json({"type": "error", "message": "Invalid user"})
                    else:
                        await websocket.send_json({"type": "error", "message": "Invalid token"})
                except Exception as e:
                    await websocket.send_json({"type": "error", "message": f"Auth failed: {e}"})

            elif msg_type == "query":
                if not authenticated_user:
                    await websocket.send_json({"type": "error", "message": "Unauthorized. Please authenticate first."})
                    continue
                text      = data.get("text", "").strip()
                thread_id = data.get("thread_id", "default")
                is_voice  = data.get("is_voice", False)
                if text:
                    asyncio.create_task(
                        nexon.process_query(text, authenticated_user.username, Assistantname, thread_id, is_voice, authenticated_user.id)
                    )

            elif msg_type == "sync_thread":
                if not authenticated_user:
                    continue
                # Frontend sends history when switching to an existing thread
                thread_id = data.get("thread_id", "default")
                messages  = data.get("messages", [])
                from Backend.AIService import load_thread_history_from_messages
                uname = authenticated_user.username if authenticated_user else "default"
                load_thread_history_from_messages(thread_id, uname, messages)
                await websocket.send_json({
                    "type":      "thread_synced",
                    "thread_id": thread_id,
                    "count":     len(messages),
                })

            elif msg_type == "delete_thread":
                if not authenticated_user:
                    continue
                thread_id = data.get("thread_id", "")
                if thread_id:
                    from Backend.AIService import clear_thread_history
                    clear_thread_history(thread_id)

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error: {e}")
        manager.disconnect(websocket)


# ── Serve React SPA (production build) ────────────────────────────────────────

@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    react_index = REACT_BUILD / "index.html"
    if REACT_BUILD.exists():
        asset_path = REACT_BUILD / full_path
        if asset_path.exists() and asset_path.is_file():
            return FileResponse(str(asset_path))
        if react_index.exists():
            return FileResponse(str(react_index))

    return JSONResponse(
        {
            "error":        "React app not built yet.",
            "instructions": "Run: cd nexon-ui && npm run build",
            "dev_mode":     "For development, run: cd nexon-ui && npm run dev",
        },
        status_code=404,
    )


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{'='*55}")
    print(f"  Nexon AI Web Server — v3.0")
    print(f"  Assistant  : {Assistantname}")
    print(f"  User       : {Username}")
    print(f"  AI Model   : Google Gemini")
    print(f"  Mode       : {DEPLOYMENT_MODE}")
    print(f"  API Docs   : http://localhost:8000/docs")
    print(f"  Database   : {'Connected (PostgreSQL)' if DB_AVAILABLE else 'Disabled (Ephemeral)'}")
    print(f"{'='*55}\n")
    init_database()
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
