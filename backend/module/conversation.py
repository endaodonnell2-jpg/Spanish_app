# backend/module/conversation.py
import os
from fastapi import FastAPI, Response, Request

def register_conversation_routes(app: FastAPI, user_memories: dict):
    # Compute the absolute path to frontend/conversation.html
    current_dir = os.path.dirname(os.path.abspath(__file__))  # backend/module/
    frontend_dir = os.path.join(current_dir, "..", "frontend")  # backend/frontend
    html_path = os.path.join(frontend_dir, "conversation.html")
    html_path = os.path.normpath(html_path)

    @app.get("/conversation", response_class=Response)
    async def conversation_page(request: Request):
        if not os.path.exists(html_path):
            return {"error": f"{html_path} does not exist!"}
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        return Response(content=html, media_type="text/html")
