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

# --- REGISTER ROUTES --- 
# Uncomment the module you want to run
register_intro_routes(app)
# register_conversation_routes(app, user_memories)


