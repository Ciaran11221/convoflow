from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatResponse
from chat import get_chat_response
import uuid

app = FastAPI(title="ConvoFlow")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: dict[str, list] = {}

@app.get("/")
def root():
    return {"status": "ConvoFlow backend running"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    if session_id not in sessions:
        sessions[session_id] = []

    # Add user message to history
    sessions[session_id].append({
        "role": "user",
        "content": req.message
    })

    # Call Claude with full conversation history
    try:
        reply = get_chat_response(sessions[session_id])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Add Claude's reply to history
    sessions[session_id].append({
        "role": "assistant",
        "content": reply
    })

    return ChatResponse(response=reply, session_id=session_id)

@app.get("/history/{session_id}")
def get_history(session_id: str):
    return {"session_id": session_id, "messages": sessions.get(session_id, [])}

@app.post("/clear/{session_id}")
def clear_session(session_id: str):
    sessions.pop(session_id, None)
    return {"cleared": session_id}