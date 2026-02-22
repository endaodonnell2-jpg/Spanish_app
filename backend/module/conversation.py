from fastapi.responses import FileResponse
from fastapi import APIRouter
import os


def register_conversation_routes(app, user_memories):

    router = APIRouter()

    # Serve the conversation page
    @router.get("/conversation")
    async def conversation_page():
        frontend_path = os.path.join("frontend", "conversation.html")
        return FileResponse(frontend_path)

    app.include_router(router)
