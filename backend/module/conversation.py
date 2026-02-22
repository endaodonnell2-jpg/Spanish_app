# backend/module/conversation.py
import os
from fastapi import FastAPI, Response, Request

def register_conversation_routes(app: FastAPI, user_memories: dict):
    # --- Absolute path to frontend/conversation.html ---
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    html_path = os.path.join(project_root, "frontend", "conversation.html")

    print("Looking for HTML at:", html_path)  # Debug to check path

    @app.get("/conversation", response_class=Response)
    async def conversation_page(request: Request):
        if not os.path.exists(html_path):
            return {"error": f"{html_path} does not exist!"}
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        return Response(content=html, media_type="text/html")

    # ---------------- Audio processing route ----------------
    @app.post("/process_audio")
    async def process_audio(request: Request):
        form = await request.form()
        if "file" not in form:
            return {"error": "No file uploaded"}
        audio_file = form["file"]
        # Here you would process the audio (send to OpenAI, TTS, etc.)
        # For now we just return a dummy TTS URL to test frontend
        return {"tts_url": "/static/test_audio.mp3"}  # <- Replace with real TTS URL
