# backend/app.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from module.conversation import register_conversation_routes
from module.intro import register_intro_routes
import uuid

# --- APP SETUP ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SHARED MEMORY START ---
user_memories = {}  # only needed for conversation module
# --- SHARED MEMORY END ---

# --- SESSION MIDDLEWARE ---
@app.middleware("http")
async def add_session_id(request: Request, call_next):
    session_id = request.cookies.get("lucas_session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    response: Response = await call_next(request)
    response.set_cookie(key="lucas_session_id", value=session_id, httponly=True)
    return response

# --- MENU SCREEN ---
@app.get("/", response_class=HTMLResponse)
async def menu():
    html_code = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Spanish App Menu</title>
        <style>
            body { font-family: sans-serif; text-align: center; padding: 50px; background: #f9f9f9; }
            button { padding: 20px 40px; font-size: 24px; margin: 20px; border-radius: 20px; cursor: pointer; border: none; color: white; }
            #intro { background-color: #2ecc71; }
            #conv { background-color: #3498db; }
        </style>
    </head>
    <body>
        <h1>Welcome to Spanish App</h1>
        <button id="intro" onclick="window.location='/intro'">Start Intro</button>
        <button id="conv" onclick="window.location='/conversation'">Start Conversation</button>
    </body>
    </html>
    """
    return HTMLResponse(html_code)

# --- REGISTER MODULE ROUTES ---
register_intro_routes(app)  # Intro module
register_conversation_routes(app, user_memories)  # Conversation module (can comment/uncomment anytime)
