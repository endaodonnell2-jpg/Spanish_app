# backend/module/conversation.py
import os
import uuid
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import JSONResponse, FileResponse
from openai import OpenAI
from gtts import gTTS

def register_conversation_routes(app: FastAPI, user_memories: dict):
    openai_client = OpenAI()

    @app.get("/conversation")
    async def conversation_page():
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../frontend/conversation.html")
        if not os.path.exists(html_path):
            return JSONResponse({"error": "conversation.html not found!"})
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()

    @app.post("/process_audio")
    async def process_audio(request: Request, file: UploadFile):
        try:
            # Identify user by session cookie
            session_id = request.cookies.get("lucas_session_id")
            if not session_id:
                session_id = str(uuid.uuid4())

            if session_id not in user_memories:
                user_memories[session_id] = []

            # Save user audio temporarily
            user_audio_path = f"/tmp/{uuid.uuid4()}.webm"
            with open(user_audio_path, "wb") as f:
                f.write(await file.read())

            # --- Convert audio to text using OpenAI (Whisper) ---
            audio_file = open(user_audio_path, "rb")
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            user_text = transcription.text
            audio_file.close()

            # Add user message to memory
            user_memories[session_id].append(f"User: {user_text}")
            if len(user_memories[session_id]) > 6:  # Keep last 3 exchanges (user + bot)
                user_memories[session_id] = user_memories[session_id][-6:]

            # --- Generate AI reply ---
            prompt = "\n".join(user_memories[session_id]) + "\nAI:"
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"system","content":"You are a friendly forthcoming person, 30 words max."},
                          {"role":"user","content":prompt}],
                max_tokens=100
            )
            ai_text = completion.choices[0].message.content.strip()

            # Add AI reply to memory
            user_memories[session_id].append(f"AI: {ai_text}")
            if len(user_memories[session_id]) > 6:
                user_memories[session_id] = user_memories[session_id][-6:]

            # --- Generate TTS ---
            tts = gTTS(ai_text, lang="en")
            tts_filename = f"/tmp/{uuid.uuid4()}.mp3"
            tts.save(tts_filename)

            return {"tts_url": f"/play_tts/{os.path.basename(tts_filename)}"}

        except Exception as e:
            return JSONResponse({"error": str(e)})

    @app.get("/play_tts/{filename}")
    async def play_tts(filename: str):
        tts_path = f"/tmp/{filename}"
        if not os.path.exists(tts_path):
            return JSONResponse({"error": "TTS file not found!"})
        return FileResponse(tts_path, media_type="audio/mpeg")
