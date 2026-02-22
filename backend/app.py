# backend/app.py
import sys
import os

# --- Ensure 'module' folder is visible ---
sys.path.append(os.path.join(os.path.dirname(__file__), "module"))

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
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

# --- REGISTER MODULE ROUTES ---
register_intro_routes(app)
register_conversation_routes(app, user_memories)
