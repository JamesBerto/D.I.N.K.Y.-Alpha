import json
import os
import secrets
from threading import Lock

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from dinky.assistant import Assistant
from dinky.audit import AuditStore
from dinky.ollama_client import OllamaClient
from dinky.storage import ConversationStore
from dinky.tools.intent import asks_device_specs, match_tool
from dinky.tools.router import ToolRouter
from dinky.voice.transcriber import SpeechTranscriber


class ChatRequest(BaseModel):
    chat_id: int = Field(gt=0)
    text: str = Field(min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    chat_id: int
    reply: str


store = ConversationStore()
audit_store = AuditStore(store.db_path)
tool_router = ToolRouter(audit_store)
model = os.getenv("DINKY_MODEL", "")
assistant = Assistant(OllamaClient(model), store)
chat_lock = Lock()
speech_transcriber = SpeechTranscriber()

token_path = store.db_path.parent / "api_token.txt"
try:
    with token_path.open("x", encoding="utf-8") as token_file:
        token_file.write(secrets.token_urlsafe(32))
except FileExistsError:
    pass

api_token = token_path.read_text(encoding="utf-8").strip()
if not api_token:
    raise RuntimeError("The local API token file is empty.")

app = FastAPI(title="D.I.N.K.Y. Local API")


def require_token(x_dinky_token: str = Header(default="")) -> None:
    if not secrets.compare_digest(x_dinky_token, api_token):
        raise HTTPException(status_code=401, detail="Invalid API token.")


def local_reply(text: str) -> str | None:
    if match_tool(text) == "system.status":
        try:
            status = tool_router.execute("system.status", "api")
        except Exception as error:
            raise HTTPException(
                status_code=503,
                detail="System status is unavailable.",
            ) from error

        reply = (
            f"CPU: {status['cpu_percent']}%. "
            f"Memory: {status['memory_percent']}%."
        )
        if status["battery_percent"] is not None:
            power = "plugged in" if status["plugged_in"] else "on battery"
            reply += f" Battery: {status['battery_percent']}%, {power}."
        return reply

    if asks_device_specs(text):
        return (
            "I can't verify your operating system or CPU model with "
            "my current tools, sir. I can check live CPU usage, memory, "
            "and battery when you ask for system status."
        )

    return None


def require_chat(chat_id: int) -> None:
    if not any(
        existing_id == chat_id
        for existing_id, _ in store.list_conversations()
    ):
        raise HTTPException(status_code=404, detail="Chat does not exist.")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/chats", dependencies=[Depends(require_token)])
def list_chats() -> dict:
    chats = [
        {"id": chat_id, "title": title}
        for chat_id, title in store.list_conversations()
    ]
    return {"chats": chats}


@app.post("/v1/chats", status_code=201, dependencies=[Depends(require_token)])
def create_chat() -> dict:
    chat_id = store.new_conversation(activate=False)
    return {"id": chat_id, "title": f"Chat {chat_id}"}


@app.get("/v1/chats/{chat_id}/messages", dependencies=[Depends(require_token)])
def chat_messages(chat_id: int) -> dict:
    require_chat(chat_id)
    return {
        "chat_id": chat_id,
        "messages": store.recent(chat_id),
    }


@app.post("/v1/chat", dependencies=[Depends(require_token)])
def chat(request: ChatRequest) -> ChatResponse:
    require_chat(request.chat_id)

    reply_from_tool = local_reply(request.text)
    if reply_from_tool is not None:
        return ChatResponse(chat_id=request.chat_id, reply=reply_from_tool)

    if not model:
        raise HTTPException(status_code=503, detail="DINKY_MODEL is not set.")

    try:
        with chat_lock:
            reply = assistant.reply(request.text, request.chat_id)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return ChatResponse(chat_id=request.chat_id, reply=reply)


@app.post("/v1/chat/stream", dependencies=[Depends(require_token)])
def chat_stream(request: ChatRequest) -> StreamingResponse:
    require_chat(request.chat_id)

    reply_from_tool = local_reply(request.text)
    if not model and reply_from_tool is None:
        raise HTTPException(status_code=503, detail="DINKY_MODEL is not set.")

    def events():
        if reply_from_tool is not None:
            event = {"type": "delta", "text": reply_from_tool}
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

            event = {"type": "done", "chat_id": request.chat_id}
            yield f"data: {json.dumps(event)}\n\n"
            return

        with chat_lock:
            try:
                for piece in assistant.stream_reply(
                    request.text, request.chat_id
                ):
                    event = {"type": "delta", "text": piece}
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

                event = {"type": "done", "chat_id": request.chat_id}
                yield f"data: {json.dumps(event)}\n\n"

            except RuntimeError as error:
                event = {"type": "error", "text": str(error)}
                yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@app.post("/v1/voice/transcribe", dependencies=[Depends(require_token)])
def transcribe_voice(audio: UploadFile = File(...)) -> dict[str, str]:
    if audio.content_type not in ("audio/wav", "audio/x-wav"):
        raise HTTPException(
            status_code=415, detail="Upload a WAV audio file."
        )

    max_bytes = 5 * 1024 * 1024
    data = audio.file.read(max_bytes + 1)

    if not data:
        raise HTTPException(status_code=400, detail="Audio file is empty.")

    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413, detail="Audio file is too large."
        )

    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise HTTPException(
            status_code=400, detail="Invalid WAV audio file."
        )

    text = speech_transcriber.transcribe(data)
    return {"text": text}


@app.get("/v1/system/status", dependencies=[Depends(require_token)])
def system_status() -> dict:
    try:
        return tool_router.execute("system.status", "api")
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="System status is unavailable.",
        ) from error


@app.get("/v1/audit", dependencies=[Depends(require_token)])
def list_audit_events() -> dict:
    return {
        "integrity_ok": audit_store.verify(),
        "events": audit_store.recent(),
    }