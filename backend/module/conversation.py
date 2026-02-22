# backend/module/conversation.py
from fastapi import FastAPI, UploadFile, File, Request, Response
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment
import uuid, os, tempfile

# --- OpenAI client ---
client = OpenAI(api_key=os.getenv("Lucas14"))
HOST_URL = os.getenv("HOST_URL", "http://localhost:10000")  # Change if deployed

def register_conversation_routes(app: FastAPI, user_memories: dict):

    # --- Serve the conversation HTML ---
    @app.get("/conversation", response_class=HTMLResponse)
    async def serve_conversation():
        # Path relative to backend/
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        html_path = os.path.join(current_dir, "frontend", "conversation.html")
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                return f.read()
        return HTMLResponse("Conversation HTML not found.", status_code=500)

    # --- Process uploaded audio ---
    @app.post("/process_audio")
    async def process_audio(request: Request, file: UploadFile = File(...)):
        session_id = request.cookies.get("lucas_session_id")
        if not session_id:
            session_id = str(uuid.uuid4())

        # --- Memory per session ---
        if session_id not in user_memories:
            user_memories[session_id] = [
                {"role": "system", "content": "You are Sarah, forthcoming, max 50 words."}
            ]
        memory = user_memories[session_id]

        file_id = uuid.uuid4().hex
        ext = file.filename.split(".")[-1].lower()
        input_path = os.path.join(tempfile.gettempdir(), f"{file_id}.{ext}")
        output_path = os.path.join(tempfile.gettempdir(), f"{file_id}.mp3")

        # Save uploaded file
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Convert WebM to WAV for Whisper
        if ext == "webm":
            wav_path = os.path.join(tempfile.gettempdir(), f"{file_id}.wav")
            AudioSegment.from_file(input_path, format="webm").export(wav_path, format="wav")
            input_for_whisper = wav_path
        else:
            input_for_whisper = input_path

        # --- Transcribe audio ---
        try:
            with open(input_for_whisper, "rb") as f:
                transcript = client.audio.transcriptions.create(model="whisper-1", file=f).text
        except Exception as e:
            if os.path.exists(input_path): os.remove(input_path)
            if ext == "webm" and os.path.exists(input_for_whisper): os.remove(input_for_whisper)
            return JSONResponse({"error": "Audio transcription failed", "details": str(e)}, status_code=400)

        # --- Append to memory ---
        memory.append({"role": "user", "content": transcript})
        if len(memory) > 13:
            user_memories[session_id] = [memory[0]] + memory[-12:]
            memory = user_memories[session_id]

        # --- GPT reply ---
        response = client.chat.completions.create(model="gpt-4o", messages=memory)
        ai_text = response.choices[0].message.content
        memory.append({"role": "assistant", "content": ai_text})

        # --- Generate TTS ---
        tts = gTTS(ai_text, lang="en")
        tts.save(output_path)

        # Cleanup input
        if os.path.exists(input_path): os.remove(input_path)
        if ext == "webm" and os.path.exists(input_for_whisper): os.remove(input_for_whisper)

        return JSONResponse({"tts_url": f"{HOST_URL}/get_audio/{file_id}"})

    # --- Serve generated audio ---
    @app.get("/get_audio/{file_id}")
    async def get_audio(file_id: str):
        file_path = os.path.join(tempfile.gettempdir(), f"{file_id}.mp3")
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="audio/mpeg")
        return JSONResponse({"error": "Audio not found"}, status_code=404)
