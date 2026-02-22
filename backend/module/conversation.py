# backend/module/conversation.py
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse

def register_conversation_routes(app: FastAPI, user_memories: dict):
    @app.get("/conversation")
    async def conversation_page():
        try:
            # Try Render's repo root if available
            root_dir = os.getenv("REPO_DIR")
            if not root_dir:
                # fallback to parent of backend folder
                root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            # Construct absolute path to conversation.html
            frontend_path = os.path.join(root_dir, "frontend", "conversation.html")

            if not os.path.exists(frontend_path):
                raise FileNotFoundError(f"{frontend_path} does not exist!")

            # Serve the HTML file
            return FileResponse(frontend_path)

        except Exception as e:
            return {"error": str(e)}
