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
user_memories = {}
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

# --- ROOT MENU ---
@app.get("/", response_class=HTMLResponse)
async def root_menu():
    html_code = """
    <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: sans-serif; display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; margin:0; background:#f0f3f5; }
                h1 { color:#2c3e50; }
                a.button { display:block; margin: 15px; padding: 20px 40px; background:#2ecc71; color:white; text-decoration:none; border-radius:30px; font-size:20px; font-weight:bold; text-align:center; }
                a.button:hover { background:#27ae60; }
            </style>
        </head>
        <body>
            <h1>Welcome to Spanish App</h1>
            <a class="button" href="/intro">Start Intro Lecture</a>
            <a class="button" href="/conversation">Start Conversation</a>
        </body>
    </html>
    """
    return HTMLResponse(html_code)

# --- REGISTER MODULES ---
register_intro_routes(app)
register_conversation_routes(app, user_memories)
