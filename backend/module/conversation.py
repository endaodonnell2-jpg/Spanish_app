# backend/module/conversation.py

import os
from fastapi.responses import FileResponse

def register_conversation_routes(app, user_memories):
    """
    Registers the /conversation route that serves the conversation.html file.
    """

    @app.get("/conversation")
    async def conversation_page():
        # Get the absolute path of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to the project root
        root_dir = os.path.dirname(current_dir)
        # Construct the full path to frontend/conversation.html
        frontend_path = os.path.join(root_dir, "frontend", "conversation.html")
        
        if not os.path.exists(frontend_path):
            return {"error": "conversation.html not found!"}
        
        return FileResponse(frontend_path)
