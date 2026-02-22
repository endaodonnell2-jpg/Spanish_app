# backend/app.py
import sys
import os
import uuid

# --- FIX: Ensure the parent directory is in sys.path ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# --- APP SETUP ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SHARED MEMORY ---
user_memories = {}  # Keep shared state for conversation

# --- SESSION MIDDLEWARE ---
@app.middleware("http")
async def add_session_id(request: Request, call_next):
    session_id = request.cookies.get("lucas_session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    response: Response = await call_next(request)
    response.set_cookie(key="lucas_session_id", value=session_id, httponly=True)
    return response

# --- ROOT MENU ---
@app.get("/", response_class=Response)
async def root_menu():
    html = """
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Spanish App Menu</title>
        <style>
          body { font-family: sans-serif; text-align:center; padding: 50px; background:#f2f2f2;}
          h1 { color:#2c3e50; }
          a { display:block; margin:20px auto; padding:20px 40px; background:#2ecc71; color:white; text-decoration:none; border-radius:15px; font-size:22px; font-weight:bold; width:200px; }
          a:hover { background:#27ae60; }
        </style>
      </head>
      <body>
        <h1>Spanish App Menu</h1>
        <a href="/intro">Intro Lesson</a>
        <a href="/conversation">Conversation</a>
      </body>
    </html>
    """
    return Response(content=html, media_type="text/html")

# --- IMPORT MODULES AND REGISTER ROUTES ---
from module.intro import register_intro_routes
from module.conversation import register_conversation_routes

register_intro_routes(app)
register_conversation_routes(app, user_memories)
