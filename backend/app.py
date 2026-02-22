from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from modules.conversation import register_conversation_routes
import uuid

from modules.intro import router as intro_router
app.include_router(intro_router)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SHARED MEMORY START ---
# Memory dictionary keyed by session ID
user_memories = {}
# --- SHARED MEMORY END ---

# --- SESSION MIDDLEWARE ---
@app.middleware("http")
async def add_session_id(request: Request, call_next):
    session_id = request.cookies.get("lucas_session_id")
    if not session_id:
        session_id = str(uuid.uuid4())  # generate new session
    response: Response = await call_next(request)
    response.set_cookie(key="lucas_session_id", value=session_id, httponly=True)
    return response

# Register conversation module
#register_conversation_routes(app, user_memories)

