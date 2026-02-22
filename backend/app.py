# backend/app.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from backend.module.conversation import register_conversation_routes
from backend.module.intro import register_intro_routes
import uuid
from fastapi.responses import HTMLResponse

# --- APP SETUP ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SHARED MEMORY ---
user_memories = {}  # only needed for conversation module

# --- SESSION MIDDLEWARE ---
@app.middleware("http")
async def add_session_id(request: Request, call_next):
    session_id = request.cookies.get("lucas_session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    response: Response = await call_next(request)
    response.set_cookie(key="lucas_session_id", value=session_id, httponly=True)
    return response

# --- OPENING MENU ---
@app.get("/", response_class=HTMLResponse)
async def root_menu():
    html_code = """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    body { font-family: sans-serif; background: #f3f3f3; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin:0; }
    .btn { padding: 20px 40px; margin: 20px; font-size: 24px; font-weight: bold; color: white; background: #2ecc71; border: none; border-radius: 20px; cursor: pointer; transition: 0.2s; }
    .btn:hover { background: #27ae60; transform: scale(1.05); }
    h1 { color: #2c3e50; }
    </style>
    <h1>Welcome to Spanish App</h1>
    <button class="btn" onclick="location.href='/intro'">Start Intro Lecture</button>
    <button class="btn" onclick="location.href='/conversation'">Start Conversation Module</button>
    """
    return HTMLResponse(html_code)

# --- REGISTER MODULE ROUTES ---
register_intro_routes(app)
register_conversation_routes(app, user_memories)
